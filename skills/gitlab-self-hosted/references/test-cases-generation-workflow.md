# Test Cases Generation Workflow

Generate test cases checklist from feature branch diff vs master.

## Usage

```
/gitlab-self-hosted test-cases <feature-branch> <project>
```

Example:
```
/gitlab-self-hosted test-cases feat/TICKET-150-my-feature my-app
```

## Workflow Steps

### 1. Fetch latest from origin
```bash
git fetch origin
```

### 2. Get diff between feature branch and master
```bash
git diff origin/master...origin/<feature-branch> --stat
git diff origin/master...origin/<feature-branch>
```

### 3. Analyze changes
- Identify modified files
- Understand business logic changes
- Note API endpoint changes
- Check database/model changes
- Review job/worker changes

### 4. Generate test cases checklist
Based on diff analysis, generate markdown with:
- Happy Cases (normal flow)
- Edge Cases (boundary conditions, error handling)

### 5. Save to plans/reports/
Save output to: `{project}/plans/reports/test-cases-{ticket}-{date}.md`

## Output Format

```markdown
# Test Cases: {TICKET} - {Description}

**Branch**: `{feature-branch}`
**Generated**: {date}
**Files Changed**: {count}

## Summary
Brief description of changes and what needs testing.

## Happy Cases

### {Feature/Component 1}
- [ ] TC-001: {Test case description}
  - **Precondition**: {setup required}
  - **Steps**: {action to perform}
  - **Expected**: {expected result}

- [ ] TC-002: {Another test case}
  - **Precondition**: ...
  - **Steps**: ...
  - **Expected**: ...

### {Feature/Component 2}
- [ ] TC-003: ...

## Edge Cases

### Error Handling
- [ ] EC-001: {Edge case description}
  - **Scenario**: {unusual condition}
  - **Expected**: {how system should handle}

### Boundary Conditions
- [ ] EC-002: {Boundary test}
  - **Scenario**: ...
  - **Expected**: ...

### Race Conditions
- [ ] EC-003: {Concurrency test}
  - **Scenario**: ...
  - **Expected**: ...

### Data Validation
- [ ] EC-004: {Invalid input test}
  - **Scenario**: ...
  - **Expected**: ...

## Regression Tests
- [ ] RT-001: Verify existing functionality still works
- [ ] RT-002: ...

## Notes
- Any special considerations
- Dependencies or blockers
```

## Analysis Guidelines

### For API Changes
- Test valid requests (happy path)
- Test invalid parameters (edge case)
- Test authentication/authorization
- Test rate limiting if applicable

### For Database/Model Changes
- Test CRUD operations
- Test validations
- Test associations
- Test migrations (up/down)

### For Job/Worker Changes
- Test successful execution
- Test idempotency
- Test failure scenarios
- Test retry behavior

### For Business Logic Changes
- Test all conditional branches
- Test boundary values
- Test null/empty inputs
- Test concurrent access

## Parameters

| Param | Description |
|-------|-------------|
| `<feature-branch>` | Feature branch to analyze (e.g., `feat/TICKET-150-xxx`) |
| `<project>` | GitLab project name |
