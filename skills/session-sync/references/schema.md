# Session Sync Frontmatter Schema

## Required Fields

| Field | Type | Source | Preserved |
|-------|------|--------|-----------|
| `type` | `claude-session` | Fixed | No |
| `project` | string | Parsed from `cwd` | No |
| `date` | `YYYY-MM-DD` | First message timestamp | No |
| `session_id` | UUID | JSONL filename | No |
| `title` | string | First user message (truncated 80 chars) | **Yes** |
| `messages` | int | Count of conversation turns | No |
| `created` | ISO 8601 | First message timestamp | No |
| `last_activity` | ISO 8601 | Last message timestamp | No |
| `cwd` | string | Working directory from JSONL | No |
| `git_branch` | string | Git branch from JSONL | No |

## Lifecycle Fields (all preserved on re-sync)

| Field | Type | Default | Values |
|-------|------|---------|--------|
| `status` | string | `active` | `active`, `done`, `blocked`, `handoff` |
| `tags` | list | `[]` | See `schema/tags.yaml` |
| `rating` | int\|null | `null` | 1-10 |
| `skills` | list | `[]` | Detected from `Skill` tool_use records |
| `comments` | string | `""` | Timestamped entries via `note`/`close`/`log` |

## Body Sections

| Section | Content | Preserved |
|---------|---------|-----------|
| `## Summary` | JSONL summary record or "No summary" | No |
| `## Skills Used` | Bullet list of detected skills | No |
| `## Artifacts` | Files created/modified as wikilinks | No |
| `## Conversation` | Full exported conversation, without body truncation | No |
| `## My Notes` | User's personal notes | **Yes** |

## Re-sync Behavior

On re-export, the renderer:
1. Reads existing file's frontmatter and `## My Notes`
2. Merges preserved fields (title, status, tags, rating, comments) with fresh data
3. Fresh data wins for non-preserved fields (messages, last_activity, etc.)
4. `## My Notes` content is carried over verbatim

## Example

```yaml
---
type: claude-session
project: ejar
date: 2026-04-14
session_id: bebe21cb-81c1-40de-adee-191dd5201bda
title: "Check implement details trong MR !9792"
messages: 15
created: 2026-04-14T02:49:47.523Z
last_activity: 2026-04-14T03:13:29.273Z
cwd: /path/to/project
git_branch: main
status: done
tags:
  - implementation
  - quick
rating: 7
skills:
  - gitlab-self-hosted
comments: |
  [2026-04-14 15:30] Good session, QC scope delivered
  [2026-04-14 15:35] [CLOSED] MR approved
---
```
