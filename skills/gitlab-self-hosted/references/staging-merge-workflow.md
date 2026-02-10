# Staging Merge Workflow

Merge feature branch to staging-k8s via temporary branch for testing.

## Usage

```
/gitlab-self-hosted staging-merge <feature-branch> <project>
```

Example:
```
/gitlab-self-hosted staging-merge feat/TICKET-150-my-feature my-app
```

## Workflow Steps

### 1. Stash local changes (if any)
```bash
git stash push -m "temp-stash-before-staging"
```

### 2. Checkout and update staging-k8s
```bash
git fetch origin
git checkout staging-k8s
git pull origin staging-k8s
```

### 3. Create temp branch and merge feature
```bash
git checkout -b temp/<ticket>-merge-to-staging-k8s
git merge origin/<feature-branch> --no-edit
```

### 4. Push temp branch
```bash
git push -u origin temp/<ticket>-merge-to-staging-k8s
```

### 5. Create MR via GitLab API
```bash
/gitlab-self-hosted create temp/<ticket>-merge-to-staging-k8s staging-k8s "<type>(<ticket>): <description>" <project>
```

### 6. Checkout back to feature branch
```bash
git checkout <feature-branch>
```

### 7. Restore stashed changes (if any)
```bash
git stash pop
```

## Branch Naming

- Temp branch: `temp/<ticket>-merge-to-staging-k8s`
- Extract ticket from feature branch name (e.g., `feat/TICKET-123-xxx` → `TICKET-123`)

## Error Handling

- If fetch fails with ref conflicts: run `git remote prune origin`
- If merge conflicts: abort and notify user
- MR title follows conventional commits format

## Parameters

| Param | Description |
|-------|-------------|
| `<feature-branch>` | Source branch to merge (e.g., `feat/TICKET-150-my-feature`) |
| `<project>` | GitLab project (e.g., `my-app`) |
