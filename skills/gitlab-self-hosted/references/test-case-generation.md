# Test Case Generation from MR

## Overview
Generate test cases by analyzing MR changes against codebase patterns.

## Workflow

### 1. Fetch MR Changes
```bash
./scripts/gitlab-mr-diff.sh <MR_IID> -p <PROJECT_ID> | jq '.changes[]'
```

### 2. Identify Changed Elements

Parse diff to find:
- New functions/methods
- Modified function signatures
- Changed conditional logic
- New error handling paths
- Database/API changes

### 3. Map to Test Types

| Change Type | Test Type |
|-------------|-----------|
| New function | Unit test |
| API endpoint | Integration test |
| Bug fix | Regression test |
| UI component | Component/E2E test |
| Config change | Smoke test |

### 4. Generate Scenarios

For each changed function:
1. **Happy path**: Normal expected input/output
2. **Edge cases**: Boundary values, empty inputs
3. **Error cases**: Invalid inputs, exceptions
4. **Integration**: Interaction with dependencies

### 5. Template Output

#### Python (pytest)
```python
def test_<function>_happy_path():
    # Arrange
    input_data = ...
    # Act
    result = function(input_data)
    # Assert
    assert result == expected

def test_<function>_edge_case():
    ...
```

#### JavaScript (Jest)
```javascript
describe('<function>', () => {
  it('should handle normal input', () => {
    expect(function(input)).toBe(expected);
  });

  it('should handle edge case', () => {
    ...
  });
});
```

## Example Analysis

Given MR with changes to `user_service.py`:
```diff
+ def validate_email(email: str) -> bool:
+     if not email or '@' not in email:
+         return False
+     return True
```

Generated test cases:
1. Valid email returns True
2. Empty string returns False
3. Email without @ returns False
4. None input handling

## Integration with Review

Include test suggestions in MR review comments:
```markdown
## Suggested Tests
- [ ] Test validate_email with valid email
- [ ] Test validate_email with empty string
- [ ] Test validate_email with missing @
```
