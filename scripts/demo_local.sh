#!/usr/bin/env bash
set -euo pipefail

api_port="${CLAIMS_API_PORT:-8010}"
uv_cache_dir="${UV_CACHE_DIR:-${TMPDIR:-/tmp}/claims-intelligence-uv-cache}"

UV_CACHE_DIR="${uv_cache_dir}" uv run claims-intelligence build-local --claims 1000 --policies 500
docker compose up --detach --build inference-api

for attempt in {1..30}; do
  if curl --silent --fail "http://localhost:${api_port}/health/ready" >/dev/null; then
    break
  fi
  if [[ "${attempt}" == "30" ]]; then
    echo "The API did not become ready. Inspect it with: docker compose logs inference-api" >&2
    exit 1
  fi
  sleep 1
done

echo "Prediction response:"
curl --silent --show-error --fail \
  --header "Content-Type: application/json" \
  --data '{
    "claim_id": "clm_demo_1042",
    "policy_tenure_days": 842,
    "claim_type": "collision",
    "reporting_delay_hours": 4.5,
    "initial_estimate": 7200,
    "prior_claim_count_365d": 1,
    "prior_paid_amount_730d": 1500,
    "damage_indicator_count": 3,
    "region_code": "ON_METRO",
    "channel": "mobile",
    "asset_age_years": 5,
    "coverage_type": "standard",
    "deductible_band": "medium"
  }' \
  "http://localhost:${api_port}/v1/predictions/claim-severity"
echo

echo "Service metrics:"
curl --silent --show-error --fail "http://localhost:${api_port}/metrics" \
  | grep '^claims_prediction_' \
  | head -n 10

echo "API documentation: http://localhost:${api_port}/docs"
echo "Stop the API with: docker compose down"
