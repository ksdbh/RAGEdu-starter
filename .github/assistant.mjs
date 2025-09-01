import { Octokit } from "octokit";
import github from "@actions/github";
import OpenAI from "openai";
import fs from "fs";
import { execSync } from "node:child_process";

const { context } = github;
const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

const owner = context.repo.owner;
const repo = context.repo.repo;

function sh(cmd) { return execSync(cmd, { stdio: "pipe" }).toString().trim(); }

async function getTrigger() {
  const body = context.payload?.comment?.body ?? "";
  if (body.startsWith("/gen")) return { type: "gen", prompt: body.replace("/gen", "").trim() };
  if (body.startsWith("/fix")) return { type: "fix", prompt: body.replace("/fix", "").trim() };
  if (body.startsWith("/scaffold")) return { type: "scaffold", prompt: body.replace("/scaffold", "").trim() };
  return { type: "gen", prompt: "Improve code quality and add missing tests." };
}

async function getRepoSnapshot(maxFiles = 80, maxBytes=45000) {
  const { data: tree } = await octokit.request("GET /repos/{owner}/{repo}/git/trees/{tree_sha}?recursive=1", {
    owner, repo, tree_sha: "HEAD"
  });
  const files = tree.tree
    .filter(t => t.type === "blob" && t.path && !t.path.startsWith(".git") && !t.path.startsWith("node_modules") && t.path.length < 4000)
    .slice(0, maxFiles)
    .map(t => t.path);

  let size=0;
  const chunks = [];
  for (const path of files) {
    try {
      const { data } = await octokit.request("GET /repos/{owner}/{repo}/contents/{path}", { owner, repo, path, ref: "HEAD" });
      if (data.type === "file" && data.content) {
        const buff = Buffer.from(data.content, data.encoding === "base64" ? "base64" : "utf8").toString("utf8");
        const block = `FILE: ${path}
-----
${buff}
`;
        if (size + block.length > maxBytes) break;
        chunks.push(block);
        size += block.length;
      }
    } catch {}
  }
  return chunks.join("\n\n");
}

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
    model: "gpt-5-thinking",
    temperature: 0.2,
    messages: [
      { role: "system", content: system },
      { role: "user", content: user }
    ],
    response_format: { type: "json_object" }
  });

  let plan;
  try { plan = JSON.parse(resp.choices[0].message.content); }
  catch (e) { console.error("JSON parse failed", e); plan = { edits: [] }; }
  const edits = Array.isArray(plan) ? plan : (plan.edits || []);
  return edits;
}

async function writeBranchAndPR(edits, title, body="Automated PR from assistant bot. Please review changes.") {
  if (!edits.length) return null;
  const branch = `assistant/${Date.now()}`;
  sh(`git checkout -b ${branch}`);

  for (const e of edits) {
    if (e.op === "delete") {
      if (fs.existsSync(e.path)) fs.rmSync(e.path, { force: true });
      try { sh(`git rm -f "${e.path}"`); } catch {}
    } else {
      fs.mkdirSync(e.path.split("/").slice(0, -1).join("/") || ".", { recursive: true });
      fs.writeFileSync(e.path, e.content ?? "", "utf8");
      sh(`git add "${e.path}"`);
    }
  }

  sh(`git config user.name "assistant-bot"`);
  sh(`git config user.email "actions@users.noreply.github.com"`);
  sh(`git commit -m "${title}"`);
  sh(`git push --set-upstream origin ${branch}`);

  const pr = await octokit.request("POST /repos/{owner}/{repo}/pulls", {
    owner, repo, title, head: branch, base: "main", body
  });

  // Optional auto-merge if label applied and PAT present
  try {
    const labels = ["automerge"];
    await octokit.request("POST /repos/{owner}/{repo}/issues/{issue_number}/labels", {
      owner, repo, issue_number: pr.data.number, labels
    });
    if (process.env.GH_AUTOMERGE_PAT) {
      const oc2 = new Octokit({ auth: process.env.GH_AUTOMERGE_PAT });
      await oc2.request("PUT /repos/{owner}/{repo}/pulls/{pull_number}/merge", {
        owner, repo, pull_number: pr.data.number, merge_method: "squash"
      });
    }
  } catch (e) { /* ignore if not configured */ }

  return pr.data.html_url;
}

(async () => {
  try {
    const trigger = await getTrigger();
    const edits = await proposeChanges(trigger);
    const url = await writeBranchAndPR(edits, `[assistant] ${trigger.type}: ${trigger.prompt.slice(0, 80)}`);
    if (context.payload?.comment?.id && url) {
      await octokit.request("POST /repos/{owner}/{repo}/issues/{issue_number}/comments", {
        owner, repo, issue_number: context.payload.issue.number, body: `Opened PR: ${url}`
      });
    }
  } catch (err) {
    console.error(err);
    process.exit(0); // don't fail the job just because we couldn't open a PR
  }
})();
