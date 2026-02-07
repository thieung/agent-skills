#!/usr/bin/env bash
# Assign/unassign GitLab MR
# Usage: ./gitlab-mr-assign.sh <MR_IID> <username> [-p PROJECT_ID]
#        ./gitlab-mr-assign.sh <MR_IID> --unassign [-p PROJECT_ID]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SCRIPT_DIR/../.env" ]]; then source "$SCRIPT_DIR/../.env"; fi

: "${GITLAB_DOMAIN:?GITLAB_DOMAIN not set}"
: "${GITLAB_TOKEN:?GITLAB_TOKEN not set}"

MR_IID="" USERNAME="" UNASSIGN=false PROJECT_ID="${GITLAB_PROJECT_ID:-}"
PROJECT_NS="${GITLAB_PROJECT_NAMESPACE:-}"

while [[ $# -gt 0 ]]; do
  case $1 in
    --unassign) UNASSIGN=true; shift ;;
    -p|--project) PROJECT_ID="$2"; shift 2 ;;
    *) [[ -z "$MR_IID" ]] && MR_IID="$1" || USERNAME="$1"; shift ;;
  esac
done

# If PROJECT_ID doesn't contain / and namespace is set, prepend namespace
if [[ -n "$PROJECT_ID" ]] && [[ ! "$PROJECT_ID" =~ "/" ]] && [[ -n "$PROJECT_NS" ]]; then
  PROJECT_ID="${PROJECT_NS}/${PROJECT_ID}"
fi

if [[ -z "$MR_IID" ]] || [[ -z "$PROJECT_ID" ]]; then
  echo '{"error": "Usage: ./gitlab-mr-assign.sh <MR_IID> <username> [-p PROJECT]"}' >&2
  exit 1
fi

encoded_project=$(echo "$PROJECT_ID" | sed 's/\//%2F/g')

if [[ "$UNASSIGN" == "true" ]]; then
  body='{"assignee_id": null}'
else
  # Get user ID from username
  user_resp=$(curl -s -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
    "${GITLAB_DOMAIN}/api/v4/users?username=${USERNAME}")
  user_id=$(echo "$user_resp" | jq -r '.[0].id // empty')

  if [[ -z "$user_id" ]]; then
    echo "{\"error\": \"User not found: $USERNAME\"}" >&2
    exit 1
  fi
  body="{\"assignee_id\": $user_id}"
fi

response=$(curl -s -w "\n%{http_code}" -X PUT \
  -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$body" \
  "${GITLAB_DOMAIN}/api/v4/projects/${encoded_project}/merge_requests/${MR_IID}")

http_code=$(echo "$response" | tail -n1)
result=$(echo "$response" | sed '$d')

if [[ "$http_code" == "200" ]]; then
  echo "$result"
else
  echo "{\"error\": \"Assign failed\", \"http_code\": $http_code}" >&2
  exit 1
fi
