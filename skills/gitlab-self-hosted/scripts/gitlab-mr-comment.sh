#!/usr/bin/env bash
# Add comment to GitLab MR
# Usage: ./gitlab-mr-comment.sh <MR_IID> "<body>" [-p PROJECT_ID]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SCRIPT_DIR/../.env" ]]; then source "$SCRIPT_DIR/../.env"; fi

: "${GITLAB_DOMAIN:?GITLAB_DOMAIN not set}"
: "${GITLAB_TOKEN:?GITLAB_TOKEN not set}"

MR_IID="" BODY="" PROJECT_ID="${GITLAB_PROJECT_ID:-}"
PROJECT_NS="${GITLAB_PROJECT_NAMESPACE:-}"

while [[ $# -gt 0 ]]; do
  case $1 in
    -p|--project) PROJECT_ID="$2"; shift 2 ;;
    *) [[ -z "$MR_IID" ]] && MR_IID="$1" || BODY="$1"; shift ;;
  esac
done

# If PROJECT_ID doesn't contain / and namespace is set, prepend namespace
if [[ -n "$PROJECT_ID" ]] && [[ ! "$PROJECT_ID" =~ "/" ]] && [[ -n "$PROJECT_NS" ]]; then
  PROJECT_ID="${PROJECT_NS}/${PROJECT_ID}"
fi

if [[ -z "$MR_IID" ]] || [[ -z "$BODY" ]] || [[ -z "$PROJECT_ID" ]]; then
  echo '{"error": "Usage: ./gitlab-mr-comment.sh <MR_IID> \"comment\" [-p PROJECT]"}' >&2
  exit 1
fi

encoded_project=$(echo "$PROJECT_ID" | sed 's/\//%2F/g')

body_json=$(jq -n --arg body "$BODY" '{body: $body}')

response=$(curl -s -w "\n%{http_code}" -X POST \
  -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$body_json" \
  "${GITLAB_DOMAIN}/api/v4/projects/${encoded_project}/merge_requests/${MR_IID}/notes")

http_code=$(echo "$response" | tail -n1)
result=$(echo "$response" | sed '$d')

if [[ "$http_code" == "201" ]]; then
  echo "$result"
else
  echo "{\"error\": \"Comment failed\", \"http_code\": $http_code}" >&2
  exit 1
fi
