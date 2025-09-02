import { Octokit } from "octokit";
import github from "@actions/github";
import OpenAI from "openai";
import fs from "fs";
import { execSync } from "node:child_process";

const { context } = github;

// before pushing
sh(`git remote set-url origin https://x-access-token:${process.env.GH_AUTOMERGE_PAT || process.env.GITHUB_TOKEN}@github.com/${owner}/${repo}.git`);
sh(`git push --set-upstream origin ${branch}`);

// Octokit: prefer PAT, fall back to GITHUB_TOKEN
const gh = new Octokit({ auth: process.env.GH_AUTOMERGE_PAT || process.env.GITHUB_TOKEN });

// OpenAI client (expects OPENAI_API_KEY secret)
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

const owner = context.repo.owner;
const repo = context.repo.repo;

function sh(cmd) {
  return execSync(cmd, { stdio: "pipe" }).toString().trim();
}

// Determine what triggered the run and extract the command/prompt
async function getTrigger() {
  // 1) Issue comment commands
  const commentBody = (context.payload?.comment?.body ?? "").trim();
  if (commentBody.startsWith("/gen")) return { type: "gen", prompt: commentBody.replace("/gen", "").trim() };
  if (commentBody.startsWith("/fix")) return { type: "fix", prompt: commentBody.replace("/fix", "").trim() };
  if (commentBody.startsWith("/scaffold")) return { type: "scaffold", prompt: commentBody.replace("/scaffold", "").trim() };

  // 2) Optional manual dispatch input (set DISPATCH_CMD in workflow env to use this)
  const dispatchCmd = (process.env.DISPATCH_CMD || "").trim();
  if (dispatchCmd) {
    const [cmd, ...rest] = dispatchCmd.split(" ");
    const prompt = rest.join(" ").trim();
    if (cmd === "/gen") return { type: "gen", prompt };
    if (cmd === "/fix") return { type: "fix", prompt };
    if (cmd === "/scaffold") return { type: "scaffold", prompt };
  }

  // 3) Fallback
  return { type: "gen", prompt: "Improve code quality and add missing tests." };
}

// Pull a lightweight repo snapshot for model context
async function getRepoSnapshot(maxFiles = 60, maxBytes = 32000) {
  const { data: tree } = await gh.request(
    "GET /repos/{owner}/{repo}/git/trees/{tree_sha}?recursive=1",
    { owner, repo, tree_sha: "HEAD" }
  );

  const files = tree.tree
    .filter(
      (t) =>
        t.type === "blob" &&
        t.path &&
        !t.path.startsWith(".git") &&
        !t.path.startsWith("node_modules") &&
        t.path.length < 4000
    )
    .slice(0, maxFiles)
    .map((t) => t.path);

  let size = 0;
  const chunks = [];
  for (const path of files) {
    try {
      const { data } = await gh.request("GET /repos/{owner}/{repo}/contents/{path}", {
        owner,
        repo,
        path,
        ref: "HEAD",
      });
      if (data.type === "file" && data.content) {
        const buff = Buffer.from(
          data.content,
          data.encoding === "base64" ? "base64" : "utf8"
        ).toString("utf8");
        const block = `FILE: ${path}\n-----\n${buff}\n`;
        if (size + block.length > maxBytes) break;
        chunks.push(block);
        size += block.length;
      }
    } catch {
      // ignore fetch errors for individual files
    }
  }
  return chunks.join("\n\n");
}

// Ask the model to propose file edits (JSON plan)
async function proposeChanges(trigger) {
  const snapshot = await getRepoSnapshot();

  const system = `You are a senior software engineer bot that edits code safely.
- Output JSON: { "edits": [ { "path": "...", "op": "create|update|delete", "content": "..." } ] }.
- Keep diffs minimal and coherent. Include unit tests when adding logic.
- Respect existing stack (FastAPI, Next.js, Terraform).`;

  const user = `
Task: ${trigger.type.toUpperCase()} — ${trigger.prompt}

Repo context (excerpt):
${snapshot}
`;

  const resp = await openai.chat.completions.create({
    model: "gpt-5-mini", // no temperature parameter for gpt-5 family
    messages: [
      { role: "system", content: system },
      { role: "user", content: user },
    ],
    response_format: { type: "json_object" },
  });

  let plan;
  try {
    plan = JSON.parse(resp.choices[0].message.content);
  } catch (e) {
    console.error("JSON parse failed", e);
    plan = { edits: [] };
  }
  const edits = Array.isArray(plan) ? plan : plan.edits || [];
  return edits;
}

// Write edits on a new branch and open a PR
async function writeBranchAndPR(
  edits,
  title,
  body = "Automated PR from assistant bot. Please review changes."
) {
  if (!edits.length) return null;

  const branch = `assistant/${Date.now()}`;
  sh(`git checkout -b ${branch}`);

  for (const e of edits) {
    if (e.op === "delete") {
      if (fs.existsSync(e.path)) fs.rmSync(e.path, { force: true });
      try {
        sh(`git rm -f "${e.path}"`);
      } catch {}
    } else {
      fs.mkdirSync(e.path.split("/").slice(0, -1).join("/") || ".", { recursive: true });
      fs.writeFileSync(e.path, e.content ?? "", "utf8");
      sh(`git add "${e.path}"`);
    }
  }

  // Configure author
  sh(`git config user.name "assistant-bot"`);
  sh(`git config user.email "actions@users.noreply.github.com"`);

  // Robust commit message handling
  const msgPath = ".git/ASSISTANT_COMMIT_MSG.txt";
  fs.writeFileSync(msgPath, title, "utf8");
  try {
    // Commit (handle "nothing to commit" gracefully)
    try {
      sh(`git commit -F "${msgPath}"`);
    } catch (e) {
      const stderr = String(e?.stderr || "");
      if (stderr.includes("nothing to commit") || stderr.includes("nothing added to commit")) {
        try { fs.unlinkSync(msgPath); } catch {}
        return null; // nothing changed; skip PR
      }
      throw e;
    }
  } finally {
    try { fs.unlinkSync(msgPath); } catch {}
  }

  // Push branch
  sh(`git push --set-upstream origin ${branch}`);

  // Open PR via PAT if available (bypasses some restrictions)
  const pr = await gh.request("POST /repos/{owner}/{repo}/pulls", {
    owner,
    repo,
    title,
    head: branch,
    base: "main", // change if your default branch differs
    body,
  });

  const prNumber = pr.data.number;

  // Try to label for automerge (optional)
  try {
    await gh.request("POST /repos/{owner}/{repo}/issues/{issue_number}/labels", {
      owner,
      repo,
      issue_number: prNumber,
      labels: ["automerge"],
    });
  } catch {
    // label may not exist / not permitted; ignore
  }

  // Optional auto-merge if PAT present and protections allow
  if (process.env.GH_AUTOMERGE_PAT) {
    try {
      await gh.request("PUT /repos/{owner}/{repo}/pulls/{pull_number}/merge", {
        owner,
        repo,
        pull_number: prNumber,
        merge_method: "squash",
      });
    } catch {
      // merge may be blocked by checks/branch protection; ignore
    }
  }

  return pr.data.html_url;
}

(async () => {
  try {
    const trigger = await getTrigger();
    const edits = await proposeChanges(trigger);
    const url = await writeBranchAndPR(
      edits,
      `[assistant] ${trigger.type}: ${trigger.prompt.slice(0, 80)}`
    );

    // If triggered by a comment, drop a link back
    if (context.payload?.comment?.id && url) {
      await gh.request("POST /repos/{owner}/{repo}/issues/{issue_number}/comments", {
        owner,
        repo,
        issue_number: context.payload.issue.number,
        body: `Opened PR: ${url}`,
      });
    }
  } catch (err) {
    console.error(err);
    // Don't fail the job hard; leave logs for debugging
    process.exit(0);
  }
})();