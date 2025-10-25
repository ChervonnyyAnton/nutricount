---
name: Task for Coding Agent
about: Well-scoped task ready for GitHub Copilot coding agent
title: "[TASK] "
labels: task, coding-agent-ready
assignees: ''
---

## Objective

<!-- Clear statement of what needs to be accomplished -->

## Context

<!-- Background information and why this task is needed -->

## Detailed Requirements

1. 
2. 
3. 

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] All tests pass
- [ ] Code follows style conventions
- [ ] Documentation updated

## Files to Modify

- **File 1**: `/path/to/file.py` - [describe changes needed]
- **File 2**: `/path/to/file.py` - [describe changes needed]
- **Tests**: `/tests/unit/test_*.py` - [describe test requirements]

## Implementation Guidance

### Similar Patterns

- Reference implementation: `/path/to/similar/code.py`
- Follow pattern from: [describe pattern]
- Reuse utility: [existing function/class]

### Code Structure

```python
# Example of desired code structure
def new_function(param1, param2):
    """
    Docstring describing function.
    
    Args:
        param1: Description
        param2: Description
        
    Returns:
        Description of return value
    """
    # Implementation
    pass
```

### Avoid

- [ ] Pattern X (use pattern Y instead)
- [ ] Hardcoded values (use config.py)
- [ ] Breaking changes without migration path

## Testing Requirements

### Unit Tests

- [ ] Test happy path
- [ ] Test edge cases
- [ ] Test error scenarios
- [ ] Mock external dependencies

### Integration Tests

- [ ] Test API endpoints
- [ ] Test database interactions
- [ ] Test with real test data

### Example Test

```python
def test_new_feature_with_valid_input(client, app):
    """Test that new feature works with valid input"""
    # Arrange
    data = {"key": "value"}
    
    # Act
    response = client.post('/api/endpoint', json=data)
    
    # Assert
    assert response.status_code == 200
    assert response.json['success'] is True
```

## Related Issues

- Depends on: #
- Related to: #
- Blocks: #

## Time Estimate

<!-- Choose one -->
- [ ] Small (1-3 hours)
- [ ] Medium (3-8 hours)
- [ ] Large (8+ hours - consider breaking down)

## Additional Notes

<!-- Any other information that would be helpful -->

---

## For Copilot Coding Agent

### Quick Summary

**What to do**: [One sentence summary]

**Where**: [Main file to change]

**How**: [Brief approach]

**Test**: [Key test to write]

### Success Criteria

Task is complete when:
1. All acceptance criteria are met
2. Tests pass with >80% coverage
3. Code follows project conventions
4. Documentation is updated
5. CI/CD pipeline passes

### Context Files to Review

Before starting, review these files:
- `/path/to/context/file1.py` - [why to review]
- `/path/to/context/file2.py` - [why to review]
- `README.md` or `ARCHITECTURE.md` - [for context]
