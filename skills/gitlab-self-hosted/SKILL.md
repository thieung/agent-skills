---
name: gitlab-self-hosted
description: GitLab Server MR workflow via REST API v4. Get MR details, create MRs, assign reviewers, post code review comments, analyze changes. READ + WRITE operations.
version: 1.0.0
license: MIT
allowed-tools:
  - Bash
---

# GitLab Self-Hosted (Server)

MR workflow via REST API v4 with PAT authentication.

## Arguments

- `auth`: Test PAT authentication
- `analyze <MR_IID> <PROJECT>`: Analyze MR (read-only, no comment)
- `get <MR_IID> <PROJECT>`: Get MR details
- `diff <MR_IID> <PROJECT>`: Get MR changes/diff
- `create <SOURCE> <TARGET> <TITLE> <PROJECT> [DESCRIPTION]`: Create new MR
- `assign <MR_IID> <USERNAME> <PROJECT>`: Assign MR to user
- `unassign <MR_IID> <PROJECT>`: Unassign MR
- `comment <MR_IID> <BODY> <PROJECT>`: Add comment to MR
- `review <MR_IID> <PROJECT>`: Full code review workflow (analyze + generate review)
- `staging-merge <FEATURE_BRANCH> <PROJECT>`: Merge feature branch to staging-k8s via temp branch
- `test-cases <FEATURE_BRANCH> <PROJECT>`: Generate test cases checklist from branch diff vs master

**PROJECT**: Can be short name (e.g., `my-app`) or full path (e.g., `group/devs/my-app`)

## Argument Handling

Parse arguments and execute corresponding script:

| Argument | Script Command |
|----------|----------------|
| `auth` | `./scripts/gitlab-auth-test.sh` |
| `analyze <IID> <PROJECT>` | `./scripts/gitlab-mr-analyze.sh <IID> -p <PROJECT>` |
| `get <IID> <PROJECT>` | `./scripts/gitlab-mr-get.sh <IID> -p <PROJECT>` |
| `diff <IID> <PROJECT>` | `./scripts/gitlab-mr-diff.sh <IID> -p <PROJECT>` |
| `create <SRC> <TGT> <TITLE> <PROJECT> [DESC]` | `./scripts/gitlab-mr-create.sh -s <SRC> -t <TGT> -T <TITLE> -p <PROJECT> [-d <DESC>]` |
| `assign <IID> <USER> <PROJECT>` | `./scripts/gitlab-mr-assign.sh <IID> <USER> -p <PROJECT>` |
| `unassign <IID> <PROJECT>` | `./scripts/gitlab-mr-assign.sh <IID> --unassign -p <PROJECT>` |
| `comment <IID> <BODY> <PROJECT>` | `./scripts/gitlab-mr-comment.sh <IID> "<BODY>" -p <PROJECT>` |
| `review <IID> <PROJECT>` | Run analyze -> read `references/code-review-workflow.md` -> generate review |
| `staging-merge <BRANCH> <PROJECT>` | Run staging merge workflow -> read `references/staging-merge-workflow.md` |
| `test-cases <BRANCH> <PROJECT>` | Generate test cases -> read `references/test-cases-generation-workflow.md` |

**Script base path**: Resolve from `SKILL.md` location (same directory as this file)

## When to Use

- Getting MR details and diffs
- Creating new MRs
- Assigning/unassigning reviewers
- Posting code review comments
- Analyzing MR changes vs codebase

**Scope: READ + WRITE operations**

## Quick Reference

### Authentication
- **Reference**: `references/authentication.md` - PAT setup, troubleshooting

### API - Merge Requests
- **Reference**: `references/api-merge-requests.md` - Get, create, update MRs

### API - Comments
- **Reference**: `references/api-notes-comments.md` - Notes, discussions

### Code Review
- **Reference**: `references/code-review-workflow.md` - Review process

### Test Case Generation
- **Reference**: `references/test-case-generation.md` - From MR analysis

### Staging Merge
- **Reference**: `references/staging-merge-workflow.md` - Merge feature to staging-k8s

### Test Cases Generation
- **Reference**: `references/test-cases-generation-workflow.md` - Generate test checklist from diff

### Helper Scripts
- `scripts/gitlab-auth-test.sh` - Validate PAT
- `scripts/gitlab-mr-get.sh <IID> -p <PROJECT>` - MR details
- `scripts/gitlab-mr-diff.sh <IID> -p <PROJECT>` - MR changes
- `scripts/gitlab-mr-create.sh -s <src> -t <tgt> -T <title>` - Create MR
- `scripts/gitlab-mr-assign.sh <IID> <user>` - Assign MR
- `scripts/gitlab-mr-comment.sh <IID> "<body>"` - Add comment

## Environment Setup

```bash
cp .env.example .env
# Edit .env with your values
```

```bash
export GITLAB_DOMAIN="https://gitlab.your-company.com"
export GITLAB_TOKEN="glpat-xxxxxxxxxxxx"
export GITLAB_PROJECT_NAMESPACE="group/subgroup"  # optional
export GITLAB_PROJECT_ID="group/project"  # optional default
```

## Workflow: Code Review

1. Get MR: `./scripts/gitlab-mr-get.sh 123 -p mygroup/myproject`
2. Get diff: `./scripts/gitlab-mr-diff.sh 123 -p mygroup/myproject`
3. Analyze changes vs codebase patterns
4. Generate review feedback
5. Post: `./scripts/gitlab-mr-comment.sh 123 "## Review..."`

## Platform Requirements

- GitLab Server with API v4
- `curl` and `jq` available
- PAT with `api` scope
