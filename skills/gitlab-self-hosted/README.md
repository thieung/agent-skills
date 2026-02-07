# GitLab Self-Hosted Skill

MR workflow via REST API v4 with PAT authentication for GitLab Server.

## Setup

### 1. Create Personal Access Token

1. Go to: `https://gitlab.your-company.com/-/user_settings/personal_access_tokens`
2. Create token with scope: `api`
3. Copy token immediately (shown only once)

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in values:

```bash
cp .env.example .env
```

Edit `.env`:
```bash
GITLAB_DOMAIN="https://gitlab.your-company.com"
GITLAB_TOKEN="glpat-xxxxxxxxxxxx"
GITLAB_PROJECT_NAMESPACE="group/subgroup"
GITLAB_PROJECT_ID=""  # Optional default project
```

## Usage

### Authentication Test

```bash
./scripts/gitlab-auth-test.sh
```

Returns user info on success, error on failure.

---

### Get MR Details

```bash
# With namespace (auto-prepends namespace/)
./scripts/gitlab-mr-get.sh 123 -p "my-app"

# With full path
./scripts/gitlab-mr-get.sh 123 -p "group/devs/my-app"
```

**Output:** JSON with title, description, author, assignees, labels, state, branches

---

### Get MR Diff/Changes

```bash
# With namespace
./scripts/gitlab-mr-diff.sh 123 -p "my-app"

# With full path
./scripts/gitlab-mr-diff.sh 456 -p "group/devs/my-frontend"
```

**Output:** JSON with `changes[]` array containing file diffs

---

### Create MR

```bash
# Basic
./scripts/gitlab-mr-create.sh \
  -s "feature-branch" \
  -t "main" \
  -T "Add new feature" \
  -p "my-app"

# With description
./scripts/gitlab-mr-create.sh \
  -s "fix/bug-123" \
  -t "develop" \
  -T "Fix login issue" \
  -d "Fixes the authentication bug reported in #123" \
  -p "my-app"
```

**Options:**
- `-s, --source` - Source branch (required)
- `-t, --target` - Target branch (required)
- `-T, --title` - MR title (required)
- `-d, --description` - MR description (optional)
- `-p, --project` - Project ID/name (required)

---

### Assign/Unassign MR

```bash
# Assign to user
./scripts/gitlab-mr-assign.sh 123 "username" -p "my-app"

# Unassign
./scripts/gitlab-mr-assign.sh 123 --unassign -p "my-app"
```

---

### Analyze MR (Read-Only)

```bash
# Analyze MR without commenting - for review before deciding
./scripts/gitlab-mr-analyze.sh 123 -p "my-app"
```

**Output:** JSON with:
- `summary`: MR title, description, state, author, branches, labels
- `stats`: files_changed, additions, deletions
- `files`: list of changed files with metadata
- `changes`: full diff for each file

---

### Add Comment to MR

```bash
# Simple comment
./scripts/gitlab-mr-comment.sh 123 "LGTM!" -p "my-app"

# Markdown comment
./scripts/gitlab-mr-comment.sh 123 "## Code Review

### Issues Found
- Missing error handling in auth module

### Suggestions
- Add try-catch block

**Status:** Needs changes" -p "my-app"
```

---

## Multi-Repo Architecture

With `GITLAB_PROJECT_NAMESPACE="group/devs"` set in `.env`:

| Command | Resolves To |
|---------|-------------|
| `-p "my-app"` | `group/devs/my-app` |
| `-p "my-frontend"` | `group/devs/my-frontend` |
| `-p "my-api-gateway"` | `group/devs/my-api-gateway` |
| `-p "group/devs/other-repo"` | `group/devs/other-repo` (full path used as-is) |

---

## Code Review Workflow

```bash
# 1. Analyze MR (read-only, all info in one call)
./scripts/gitlab-mr-analyze.sh 123 -p "my-app" | jq '.summary, .stats'

# 2. Review changes
./scripts/gitlab-mr-analyze.sh 123 -p "my-app" | jq '.files[].path'

# 3. Post review comment (after analysis)
./scripts/gitlab-mr-comment.sh 123 "## Review Complete

- Code quality: Good
- Tests: Passing
- Ready to merge" -p "my-app"
```

---

## Staging Merge Workflow

Merge feature branch to `staging-k8s` via temporary branch for testing.

```bash
/gitlab-self-hosted staging-merge feat/TICKET-150-my-feature my-app
```

**Steps:**
1. Stash local changes
2. Checkout & update `staging-k8s`
3. Create temp branch `temp/<ticket>-merge-to-staging-k8s`
4. Merge feature branch
5. Push & create MR
6. Checkout back to feature branch
7. Restore stashed changes

---

## Test Cases Generation Workflow

Generate test cases checklist from feature branch diff vs master.

```bash
/gitlab-self-hosted test-cases feat/TICKET-150-my-feature my-app
```

**Output format:**
- **Happy Cases**: Normal flow tests with checkbox
- **Edge Cases**: Boundary, error handling, race conditions
- **Regression Tests**: Verify existing functionality

**Saves to:** `{project}/plans/reports/test-cases-{ticket}-{date}.md`

---

## Error Handling

All scripts return JSON errors to stderr:

```json
{"error": "Authentication failed", "http_code": 401}
{"error": "Failed to get MR", "http_code": 404}
{"error": "User not found: unknown_user"}
```

Exit codes:
- `0` - Success
- `1` - Failure

---

## References

- `references/authentication.md` - PAT setup guide
- `references/api-merge-requests.md` - MR API reference
- `references/api-notes-comments.md` - Comments API
- `references/code-review-workflow.md` - Review process
- `references/test-case-generation.md` - Test generation from MR
- `references/staging-merge-workflow.md` - Merge feature to staging-k8s
- `references/test-cases-generation-workflow.md` - Generate test checklist

---

## Platform Requirements

- GitLab Server with API v4
- `curl` and `jq` available
- PAT with `api` scope
