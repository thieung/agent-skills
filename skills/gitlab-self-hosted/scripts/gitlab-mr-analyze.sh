#!/usr/bin/env bash
# Analyze GitLab MR for review (read-only, no comment)
# Usage: ./gitlab-mr-analyze.sh <MR_IID> [-p PROJECT_ID]
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
  echo '{"error": "MR IID required. Usage: ./gitlab-mr-analyze.sh 123 [-p PROJECT_ID]"}' >&2
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

# Fetch MR details
mr_response=$(curl -s -w "\n%{http_code}" \
  -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "${GITLAB_DOMAIN}/api/v4/projects/${encoded_project}/merge_requests/${MR_IID}")

mr_code=$(echo "$mr_response" | tail -n1)
mr_body=$(echo "$mr_response" | sed '$d')

if [[ "$mr_code" != "200" ]]; then
  echo "{\"error\": \"Failed to get MR\", \"http_code\": $mr_code}" >&2
  exit 1
fi

# Fetch MR changes
changes_response=$(curl -s -w "\n%{http_code}" \
  -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "${GITLAB_DOMAIN}/api/v4/projects/${encoded_project}/merge_requests/${MR_IID}/changes")

changes_code=$(echo "$changes_response" | tail -n1)
changes_body=$(echo "$changes_response" | sed '$d')

if [[ "$changes_code" != "200" ]]; then
  echo "{\"error\": \"Failed to get MR changes\", \"http_code\": $changes_code}" >&2
  exit 1
fi

# Output combined analysis
jq -n \
  --argjson mr "$mr_body" \
  --argjson changes "$changes_body" \
  '{
    summary: {
      iid: $mr.iid,
      title: $mr.title,
      description: $mr.description,
      state: $mr.state,
      author: $mr.author.username,
      assignee: ($mr.assignee.username // null),
      source_branch: $mr.source_branch,
      target_branch: $mr.target_branch,
      labels: $mr.labels,
      web_url: $mr.web_url,
      created_at: $mr.created_at,
      updated_at: $mr.updated_at
    },
    stats: {
      files_changed: ($changes.changes | length),
      additions: ($changes.changes | map(.diff | split("\n") | map(select(startswith("+"))) | length) | add),
      deletions: ($changes.changes | map(.diff | split("\n") | map(select(startswith("-"))) | length) | add)
    },
    files: [
      $changes.changes[] | {
        path: .new_path,
        old_path: (if .old_path != .new_path then .old_path else null end),
        new_file: .new_file,
        renamed_file: .renamed_file,
        deleted_file: .deleted_file
      }
    ],
    changes: $changes.changes
  }'
