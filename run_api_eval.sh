#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   API_KEY=xxx ./run_api_eval.sh
# Optional:
#   BASE_URL=https://your-proxy.example/v1
#   TEMPERATURE=0.7
#   PER_LEVEL=25
#   SEED=2026

BASE_URL="${BASE_URL:-https://api.openai.com/v1}"
TEMPERATURE="${TEMPERATURE:-0.7}"
PER_LEVEL="${PER_LEVEL:-25}"
SEED="${SEED:-2026}"

API_KEY="${API_KEY:-${OPENAI_API_KEY:-}}"

if [[ -z "${API_KEY}" ]]; then
  echo "Error: API_KEY or OPENAI_API_KEY is not set."
  echo "Example: API_KEY='your_key' ./run_api_eval.sh"
  exit 1
fi

python eval_api.py \
  --api-key "${API_KEY}" \
  --base-url "${BASE_URL}" \
  --temperature "${TEMPERATURE}" \
  --per-level "${PER_LEVEL}" \
  --seed "${SEED}" \
  --input MathSticks_bench_400.jsonl \
  --subset MathSticks_bench_100.jsonl \
  --image-dir ./image \
  --output-dir ./baseline_eval_results_100_subset \
  --rebuild-subset \
  --resume
