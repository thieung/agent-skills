# API - Merge Requests

## Endpoints

### Get MR Details
```
GET /api/v4/projects/:id/merge_requests/:iid
```

**Response fields:**
- `iid` - Project-scoped ID
- `title`, `description`
- `state` - opened, closed, merged
- `author`, `assignee`, `assignees`
- `source_branch`, `target_branch`
- `labels`, `milestone`
- `web_url`

### Get MR Changes/Diff
```
GET /api/v4/projects/:id/merge_requests/:iid/changes
```

**Response includes:**
- All MR details plus `changes[]` array
- Each change: `old_path`, `new_path`, `diff`
- Flags: `new_file`, `renamed_file`, `deleted_file`

### Create MR
```
POST /api/v4/projects/:id/merge_requests
```

**Required body:**
```json
{
  "source_branch": "feature-branch",
  "target_branch": "main",
  "title": "MR Title"
}
```

**Optional:**
- `description` - MR description
- `assignee_id` - User ID to assign
- `labels` - Comma-separated labels

### Update MR
```
PUT /api/v4/projects/:id/merge_requests/:iid
```

**Body options:**
- `assignee_id` - Change assignee (null to unassign)
- `title`, `description` - Update text
- `labels` - Update labels
- `state_event` - "close" or "reopen"

## Project ID Format

| Format | Example |
|--------|---------|
| Numeric ID | `42` |
| URL-encoded path | `group%2Fproject` |
| Path with / | Encode as `%2F` |

## Helper Scripts

```bash
# Get MR details
./scripts/gitlab-mr-get.sh 123 -p mygroup/myproject

# Get MR diff
./scripts/gitlab-mr-diff.sh 123 -p mygroup/myproject

# Create MR
./scripts/gitlab-mr-create.sh \
  -s feature-branch \
  -t main \
  -T "Add new feature" \
  -d "Description here" \
  -p mygroup/myproject

# Assign MR
./scripts/gitlab-mr-assign.sh 123 username -p mygroup/myproject

# Unassign MR
./scripts/gitlab-mr-assign.sh 123 --unassign -p mygroup/myproject
```

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success (GET, PUT) |
| 201 | Created (POST) |
| 404 | MR or project not found |
| 403 | Permission denied |
