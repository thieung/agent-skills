# GitLab Self-Hosted Skill

MR workflow via REST API v4 with PAT authentication for GitLab Server.

## Setup

### 1. Create Personal Access Token

1. Go to: `https://<your-gitlab-domain>/-/user_settings/personal_access_tokens`
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
/gitlab-self-hosted auth
```

Returns user info on success, error on failure.

---

### Get MR Details

```bash
# With namespace (auto-prepends GITLAB_PROJECT_NAMESPACE)
/gitlab-self-hosted get 123 my-app

# With full path
/gitlab-self-hosted get 123 group/subgroup/my-app
```

**Output:** JSON with title, description, author, assignees, labels, state, branches

---

### Get MR Diff/Changes

```bash
# With namespace
/gitlab-self-hosted diff 123 my-app

# With full path
/gitlab-self-hosted diff 456 group/subgroup/my-frontend
```

**Output:** JSON with `changes[]` array containing file diffs

---

### Create MR

```bash
# Basic
/gitlab-self-hosted create feature-branch main "Add new feature" my-app

# With description
/gitlab-self-hosted create fix/bug-123 develop "Fix login issue" my-app "Fixes the authentication bug reported in #123"
```

**Arguments:** `create <SOURCE> <TARGET> <TITLE> <PROJECT> [DESCRIPTION]`

---

### Assign/Unassign MR

```bash
# Assign to user
/gitlab-self-hosted assign 123 username my-app

# Unassign
/gitlab-self-hosted unassign 123 my-app
```

---

### Analyze MR (Read-Only)

```bash
# Analyze MR without commenting - for review before deciding
/gitlab-self-hosted analyze 123 my-app
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
/gitlab-self-hosted comment 123 "LGTM!" my-app

# Markdown comment
/gitlab-self-hosted comment 123 "## Code Review

### Issues Found
- Missing error handling in auth module

### Suggestions
- Add try-catch block

**Status:** Needs changes" my-app
```

---

### Code Review (Full Workflow)

```bash
/gitlab-self-hosted review 123 my-app
```

Runs analyze, reads `references/code-review-workflow.md`, generates review.

---

## Multi-Repo Architecture

With `GITLAB_PROJECT_NAMESPACE="group/subgroup"` set in `.env`:

| Command | Resolves To |
|---------|-------------|
| `my-app` | `group/subgroup/my-app` |
| `my-frontend` | `group/subgroup/my-frontend` |
| `my-api-gateway` | `group/subgroup/my-api-gateway` |
| `group/subgroup/other-repo` | `group/subgroup/other-repo` (full path used as-is) |

---

## Code Review Workflow

```bash
# 1. Analyze MR (read-only, all info in one call)
/gitlab-self-hosted analyze 123 my-app

# 2. Full review (analyze + generate review + post comment)
/gitlab-self-hosted review 123 my-app

# 3. Post manual comment
/gitlab-self-hosted comment 123 "## Review Complete

- Code quality: Good
- Tests: Passing
- Ready to merge" my-app
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
