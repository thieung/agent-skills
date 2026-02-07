# Code Review Workflow

## Overview
Process for reviewing GitLab MRs with Claude.

## Step-by-Step

### 1. Fetch MR Context
```bash
./scripts/gitlab-mr-get.sh <MR_IID> -p <PROJECT_ID>
```
Extract: title, description, author, labels, source/target branches

### 2. Get Changes
```bash
./scripts/gitlab-mr-diff.sh <MR_IID> -p <PROJECT_ID>
```
Response contains `changes[]` with:
- old_path, new_path
- diff (unified format)
- new_file, renamed_file, deleted_file flags

### 3. Analyze Changes

Review each changed file for:
- Code quality issues
- Potential bugs
- Security vulnerabilities
- Missing error handling
- Performance concerns
- Test coverage gaps
- Style/convention violations

### 4. Generate Feedback

Format review as markdown:
```markdown
## MR Review: [Title]

### Summary
Brief overview of changes and overall assessment.

### Issues Found
- **[Critical]** Description...
- **[Warning]** Description...

### Suggestions
- Consider...

### Positive Feedback
- Good use of...
```

### 5. Post Comment
```bash
./scripts/gitlab-mr-comment.sh <MR_IID> "<feedback>" -p <PROJECT_ID>
```

## Review Checklist

- [ ] All files reviewed
- [ ] Security concerns addressed
- [ ] Test coverage considered
- [ ] Performance implications checked
- [ ] Documentation updates needed?
