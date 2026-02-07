#!/usr/bin/env bash
# Validate GitLab PAT authentication
# Usage: ./gitlab-auth-test.sh
# Exit: 0=success, 1=failure
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load .env if exists
if [[ -f "$SCRIPT_DIR/../.env" ]]; then
  source "$SCRIPT_DIR/../.env"
elif [[ -f "$SCRIPT_DIR/.env" ]]; then
  source "$SCRIPT_DIR/.env"
fi

# Validate required vars
: "${GITLAB_DOMAIN:?Error: GITLAB_DOMAIN not set}"
: "${GITLAB_TOKEN:?Error: GITLAB_TOKEN not set}"

# Test authentication (GitLab uses PRIVATE-TOKEN header)
response=$(curl -s -w "\n%{http_code}" \
  -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "${GITLAB_DOMAIN}/api/v4/user")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [[ "$http_code" == "200" ]]; then
  echo "$body"
  exit 0
else
  echo "{\"error\": \"Authentication failed\", \"http_code\": $http_code}" >&2
  exit 1
fi
