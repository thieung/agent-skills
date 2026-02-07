#!/usr/bin/env bash
# Create GitLab MR
# Usage: ./gitlab-mr-create.sh -s <source> -t <target> -T <title> [-d <desc>] [-p PROJECT_ID]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SCRIPT_DIR/../.env" ]]; then source "$SCRIPT_DIR/../.env"; fi

: "${GITLAB_DOMAIN:?GITLAB_DOMAIN not set}"
: "${GITLAB_TOKEN:?GITLAB_TOKEN not set}"

SOURCE="" TARGET="" TITLE="" DESC="" PROJECT_ID="${GITLAB_PROJECT_ID:-}"
PROJECT_NS="${GITLAB_PROJECT_NAMESPACE:-}"

while [[ $# -gt 0 ]]; do
  case $1 in
    -s|--source) SOURCE="$2"; shift 2 ;;
    -t|--target) TARGET="$2"; shift 2 ;;
    -T|--title) TITLE="$2"; shift 2 ;;
    -d|--description) DESC="$2"; shift 2 ;;
    -p|--project) PROJECT_ID="$2"; shift 2 ;;
    *) shift ;;
  esac
done

# If PROJECT_ID doesn't contain / and namespace is set, prepend namespace
if [[ -n "$PROJECT_ID" ]] && [[ ! "$PROJECT_ID" =~ "/" ]] && [[ -n "$PROJECT_NS" ]]; then
  PROJECT_ID="${PROJECT_NS}/${PROJECT_ID}"
fi

if [[ -z "$SOURCE" ]] || [[ -z "$TARGET" ]] || [[ -z "$TITLE" ]] || [[ -z "$PROJECT_ID" ]]; then
  echo '{"error": "Required: -s source -t target -T title -p project"}' >&2
  exit 1
fi

encoded_project=$(echo "$PROJECT_ID" | sed 's/\//%2F/g')

body=$(jq -n \
  --arg s "$SOURCE" --arg t "$TARGET" --arg title "$TITLE" --arg desc "$DESC" \
  '{source_branch: $s, target_branch: $t, title: $title, description: $desc}')

response=$(curl -s -w "\n%{http_code}" -X POST \
  -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$body" \
  "${GITLAB_DOMAIN}/api/v4/projects/${encoded_project}/merge_requests")

http_code=$(echo "$response" | tail -n1)
result=$(echo "$response" | sed '$d')

if [[ "$http_code" == "201" ]]; then
  echo "$result"
else
  echo "{\"error\": \"MR creation failed\", \"http_code\": $http_code, \"details\": $result}" >&2
  exit 1
fi
