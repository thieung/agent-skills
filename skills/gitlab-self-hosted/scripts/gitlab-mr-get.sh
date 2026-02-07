#!/usr/bin/env bash
# Get GitLab MR details
# Usage: ./gitlab-mr-get.sh <MR_IID> [-p PROJECT_ID]
# Exit: 0=success, 1=failure
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load .env
if [[ -f "$SCRIPT_DIR/../.env" ]]; then
  source "$SCRIPT_DIR/../.env"
elif [[ -f "$SCRIPT_DIR/.env" ]]; then
  source "$SCRIPT_DIR/.env"
fi

: "${GITLAB_DOMAIN:?Error: GITLAB_DOMAIN not set}"
: "${GITLAB_TOKEN:?Error: GITLAB_TOKEN not set}"

MR_IID=""
PROJECT_ID="${GITLAB_PROJECT_ID:-}"
PROJECT_NS="${GITLAB_PROJECT_NAMESPACE:-}"

# Parse args
while [[ $# -gt 0 ]]; do
  case $1 in
    -p|--project) PROJECT_ID="$2"; shift 2 ;;
    *) MR_IID="$1"; shift ;;
  esac
done

if [[ -z "$MR_IID" ]]; then
  echo '{"error": "MR IID required. Usage: ./gitlab-mr-get.sh 123 [-p PROJECT_ID]"}' >&2
  exit 1
fi

# If PROJECT_ID doesn't contain / and namespace is set, prepend namespace
if [[ -n "$PROJECT_ID" ]] && [[ ! "$PROJECT_ID" =~ "/" ]] && [[ -n "$PROJECT_NS" ]]; then
  PROJECT_ID="${PROJECT_NS}/${PROJECT_ID}"
fi

if [[ -z "$PROJECT_ID" ]]; then
  echo '{"error": "PROJECT_ID required (env or -p flag)"}' >&2
  exit 1
fi

# URL-encode project ID if it contains /
encoded_project=$(echo "$PROJECT_ID" | sed 's/\//%2F/g')

response=$(curl -s -w "\n%{http_code}" \
  -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "${GITLAB_DOMAIN}/api/v4/projects/${encoded_project}/merge_requests/${MR_IID}")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [[ "$http_code" == "200" ]]; then
  echo "$body"
  exit 0
else
  echo "{\"error\": \"Failed to get MR\", \"http_code\": $http_code}" >&2
  exit 1
fi
