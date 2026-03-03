#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:3000}"
JOB_ID="finance-hourly-e2e-full-$(date +%s)"
E2E_TIMEOUT_SECONDS="${E2E_TIMEOUT_SECONDS:-900}"

curl -sS -X POST "$BASE_URL/api/jobs/trigger" \
  -H 'Content-Type: application/json' \
  -d "{\"job_id\":\"$JOB_ID\",\"ingestor_plugin\":\"finance\",\"analyzer_plugin\":{\"provider\":\"ollama\",\"model\":\"llama3\",\"temperature\":0.2,\"prompt_template_id\":\"finance-v1\"},\"pipeline_settings\":{\"max_parallelism\":8,\"max_retries\":3,\"cron\":\"0 * * * *\"},\"storage_policy\":{\"raw_retention_days\":30,\"analyzed_retention_days\":365,\"persist_artifacts\":true}}" >/dev/null

echo "Triggered $JOB_ID; waiting for analysis completion logs..."

python3 - <<PY
import json
import time
import requests

base_url = "${BASE_URL}"
job_id = "${JOB_ID}"

for i in range(${E2E_TIMEOUT_SECONDS}):
    time.sleep(1)
    logs = requests.get(f"{base_url}/api/observability/logs", params={"job_id": job_id}, timeout=10).json().get("logs", [])
    msgs = [x.get("message", "") for x in logs]
    if any("Analysis complete" in m for m in msgs):
        print(json.dumps({"job_id": job_id, "status": "ok", "log_count": len(logs)}, indent=2))
        raise SystemExit(0)
    if any("Analysis failed" in m for m in msgs):
        print(json.dumps({"job_id": job_id, "status": "failed", "logs": logs[:8]}, indent=2))
        raise SystemExit(1)

print(json.dumps({"job_id": job_id, "status": "timeout"}, indent=2))
raise SystemExit(1)
PY
