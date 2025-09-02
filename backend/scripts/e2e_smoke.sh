#!/usr/bin/env bash
set -euo pipefail

# Simple e2e smoke script for the backend API.
# - GET /health and assert JSON contains {"ok": true}
# - POST /rag/answer with a test question and save response to resp.json
# - Validate resp.json contains an "answer" key and that "citations" is a list

HEALTH_URL="http://localhost:8000/health"
RAG_ANSWER_URL="http://localhost:8000/rag/answer"
POST_BODY='{"q":"Test question about algorithms"}'
RESP_FILE="resp.json"

echo "==> Checking health endpoint: ${HEALTH_URL}"
health_resp=$(curl -sS --fail "${HEALTH_URL}" || true)
if [ -z "${health_resp}" ]; then
  echo "Health request failed or returned empty response"
  exit 1
fi

echo "Health response: ${health_resp}"

# Validate health JSON contains {"ok": true}
python - <<PY
import sys, json
try:
    j = json.loads('''"""%s"""''' % sys.stdin.read())
except Exception as e:
    print('Failed to parse health response as JSON:', e)
    sys.exit(2)
if j.get('ok') is not True:
    print('Health check failed: expected key "ok" == true, got:', j)
    sys.exit(1)
print('Health check OK')
PY <<PY_INPUT
${health_resp}
PY_INPUT

# POST the test question and save response
echo "==> Posting test question to ${RAG_ANSWER_URL}"
curl -sS --fail -X POST -H "Content-Type: application/json" -d "${POST_BODY}" "${RAG_ANSWER_URL}" -o "${RESP_FILE}"

if [ ! -s "${RESP_FILE}" ]; then
  echo "Empty or missing response file ${RESP_FILE}"
  exit 1
fi

echo "Saved POST response to ${RESP_FILE}"

# Validate response JSON has "answer" and "citations" is a list
python - <<PY
import sys, json
try:
    j = json.load(open('${RESP_FILE}'))
except Exception as e:
    print('Failed to load JSON from ${RESP_FILE}:', e)
    sys.exit(2)
if 'answer' not in j:
    print('Response JSON missing "answer" key:', j)
    sys.exit(1)
if not isinstance(j.get('citations'), list):
    print('Response JSON "citations" is not a list (got type %s):' % type(j.get('citations')) , j.get('citations'))
    sys.exit(1)
print('RAG response validation OK: contains "answer" and list "citations"')
PY

echo "All smoke checks passed"
