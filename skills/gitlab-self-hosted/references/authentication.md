# Authentication

## Overview
GitLab uses Personal Access Tokens (PAT) with `PRIVATE-TOKEN` header.

## Create PAT

1. Go to GitLab: `Settings > Access Tokens`
2. Click "Add new token"
3. Set name: e.g., "Claude Code MR Access"
4. Set expiration: max 1 year recommended
5. Select scopes: `api` (full read/write)
6. Click "Create personal access token"
7. Copy token immediately (shown only once)

## Token Format
```
glpat-xxxxxxxxxxxxxxxxxxxx
```

## Environment Variables

```bash
# Required
export GITLAB_DOMAIN="https://gitlab.your-company.com"
export GITLAB_TOKEN="glpat-xxxxxxxxxxxx"

# Optional default project
export GITLAB_PROJECT_ID="group/project"
```

Or create `.env` file in skill directory:
```bash
GITLAB_DOMAIN="https://gitlab.your-company.com"
GITLAB_TOKEN="glpat-xxxxxxxxxxxx"
GITLAB_PROJECT_ID=""
```

## API Header
```bash
curl -H "PRIVATE-TOKEN: $GITLAB_TOKEN" "$GITLAB_DOMAIN/api/v4/user"
```

## Test Authentication
```bash
./scripts/gitlab-auth-test.sh
```

Success returns user JSON with username, email.
Failure returns error with http_code.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Check token is valid and not expired |
| SSL/TLS errors | Set `CURL_CA_BUNDLE` for custom CA |
| Connection timeout | Check VPN/network access |
| 403 Forbidden | Token lacks required scope |

## Security Best Practices

- Use minimal required scope (`api` for full access)
- Set token expiration
- Store in env vars, never commit
- Add `.env` to `.gitignore`
