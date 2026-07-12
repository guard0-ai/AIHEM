#!/usr/bin/env bash
# Provision the Meeseeks n8n runtime: owner account, scenario workflows, and
# activation. Idempotent-ish — safe to re-run. Requires docker (for CLI activate
# + restart) and python3.
#
#   ./provision.sh            # uses localhost:5678 / aihem-meeseeks-n8n
set -euo pipefail

N8N="${N8N_URL:-http://localhost:5678}"
CONTAINER="${N8N_CONTAINER:-aihem-meeseeks-n8n}"
DIR="$(cd "$(dirname "$0")" && pwd)/workflows"
J="$(mktemp)"

echo "waiting for n8n at $N8N ..."
for _ in $(seq 1 60); do curl -sf "$N8N/healthz" >/dev/null 2>&1 && break; sleep 1; done

# Owner: try first-run setup, fall back to login if already set up.
if ! curl -s -c "$J" -X POST "$N8N/rest/owner/setup" -H 'content-type: application/json' \
      -d '{"email":"lab@meeseeks.local","firstName":"Lab","lastName":"Admin","password":"MeeseeksLab1"}' \
      | grep -q '"id"'; then
  curl -s -c "$J" -X POST "$N8N/rest/login" -H 'content-type: application/json' \
      -d '{"emailOrLdapLoginId":"lab@meeseeks.local","password":"MeeseeksLab1"}' >/dev/null
fi

# Import + activate each scenario workflow.
for f in "$DIR"/*.json; do
  [ -e "$f" ] || continue
  name="$(python3 -c "import json;print(json.load(open('$f'))['name'])")"
  existing="$(curl -s -b "$J" "$N8N/rest/workflows" \
    | python3 -c "import sys,json;ws=json.load(sys.stdin).get('data',[]);print(next((w['id'] for w in ws if w['name']=='$name'),''))")"
  if [ -n "$existing" ]; then
    wid="$existing"
  else
    wid="$(curl -s -b "$J" -X POST "$N8N/rest/workflows" -H 'content-type: application/json' \
      --data @"$f" | python3 -c "import sys,json;print(json.load(sys.stdin)['data']['id'])")"
  fi
  echo "  workflow '$name' -> $wid"
  docker exec "$CONTAINER" n8n update:workflow --id="$wid" --active=true >/dev/null 2>&1 || true
done

echo "restarting n8n to register webhooks ..."
docker restart "$CONTAINER" >/dev/null
for _ in $(seq 1 60); do curl -sf "$N8N/healthz" >/dev/null 2>&1 && break; sleep 1; done
sleep 4  # webhook routes register a moment after healthz goes green
rm -f "$J"
echo "provisioned. scenario webhooks are live at $N8N/webhook/<scenario>"
