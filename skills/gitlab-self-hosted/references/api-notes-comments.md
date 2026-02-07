# API - Notes & Comments

## Overview
GitLab uses "Notes" for comments on MRs, issues, etc.

## Endpoints

### Add Comment to MR
```
POST /api/v4/projects/:id/merge_requests/:iid/notes
```

**Body:**
```json
{
  "body": "Your comment here. **Markdown** supported."
}
```

**Response:**
```json
{
  "id": 123,
  "body": "Your comment here...",
  "author": {...},
  "created_at": "2024-01-01T00:00:00Z"
}
```

### List MR Comments
```
GET /api/v4/projects/:id/merge_requests/:iid/notes
```

Returns array of notes ordered by creation date.

### Update Comment
```
PUT /api/v4/projects/:id/merge_requests/:iid/notes/:note_id
```

**Body:**
```json
{
  "body": "Updated comment"
}
```

### Delete Comment
```
DELETE /api/v4/projects/:id/merge_requests/:iid/notes/:note_id
```

## Markdown Support

GitLab notes support full markdown:
- Headers, bold, italic
- Code blocks with syntax highlighting
- Lists, tables
- Mentions: `@username`
- Issue refs: `#123`
- MR refs: `!456`

## Helper Script

```bash
# Add comment
./scripts/gitlab-mr-comment.sh 123 "## Review Comment

- Issue found
- Suggestion here" -p mygroup/myproject
```

## Discussions (Threaded)

For threaded discussions:
```
POST /api/v4/projects/:id/merge_requests/:iid/discussions
```

Body same as notes. Creates new discussion thread.

## Error Codes

| Code | Meaning |
|------|---------|
| 201 | Comment created |
| 200 | Comment updated |
| 404 | MR or note not found |
| 403 | Cannot modify others' notes |
