# {filename}.py

**Version:** {YYYY-MM-DD_R}  
**Module:** {Module name}  
**Layer:** {Architecture layer (Gateway/Interface/Core)}  
**Dependencies:** {List dependencies}

---

## PURPOSE

{Brief description of what this module does - 2-3 sentences}

---

## ARCHITECTURE

### Module Position

**Layer:** {Gateway/Interface/Core}  
**Subsystem:** {Subsystem name}  
**Interfaces:** {Interfaces it implements/uses}

### Integration Points

**Imports from:**
- {module1} - {What it uses}
- {module2} - {What it uses}

**Imported by:**
- {module1} - {How it's used}
- {module2} - {How it's used}

### Design Patterns

**Patterns used:**
- {Pattern name} - {Why used}
- {Pattern name} - {Why used}

---

## FUNCTIONS

### {function_name}()

**Purpose:** {What this function does}

**Signature:**
```python
def {function_name}(
    param1: {Type},
    param2: {Type},
    param3: {Type} = {default}
) -> {ReturnType}:
```

**Parameters:**
- `param1` - {Type and description}
- `param2` - {Type and description}
- `param3` - {Type and description} (optional, default: {value})

**Returns:** {What it returns and when}

**Raises:**
- `{ExceptionType}` - {When and why}
- `{ExceptionType}` - {When and why}

**Behavior:**
1. {Step 1 description}
2. {Step 2 description}
3. {Step 3 description}
4. {Step 4 description}

**Usage:**
```python
result = {function_name}(
    param1_value,
    param2_value,
    param3=custom_value
)
```

**Performance:** {Timing expectations}

**Error Scenarios:**
- {Scenario 1} → {What happens}
- {Scenario 2} → {What happens}

---

### {function_name_2}()

{Repeat above structure for each function}

---

## USAGE EXAMPLES

### Basic Usage

```python
# Example 1: {Description}
{code example}

# Expected output:
# {output description}
```

### Advanced Usage

```python
# Example 2: {Description}
{code example}

# Expected output:
# {output description}
```

### Error Handling

```python
# Example 3: {Description}
try:
    {code example}
except {ExceptionType} as e:
    # Handle error
    {error handling}
```

---

## ERROR HANDLING

### Exception Types

**{ExceptionType}:**
- **When:** {Condition that raises it}
- **Why:** {Reason for exception}
- **Handle:** {How to handle it}

**{ExceptionType}:**
- **When:** {Condition that raises it}
- **Why:** {Reason for exception}
- **Handle:** {How to handle it}

### Error Recovery

**Strategy:**
1. {Recovery step 1}
2. {Recovery step 2}
3. {Fallback behavior}

**Circuit Breaker:**
- Enabled: {Yes/No}
- Threshold: {Number of failures}
- Timeout: {Duration}

---

## PERFORMANCE

### Timing

**Expected Performance:**
- Cold start: {time}ms
- Warm start: {time}ms
- Average call: {time}ms
- 95th percentile: {time}ms

**Performance Factors:**
- {Factor 1} - {Impact}
- {Factor 2} - {Impact}

### Optimization

**Current Optimizations:**
- {Optimization 1} - {Benefit}
- {Optimization 2} - {Benefit}

**Future Improvements:**
- {Potential improvement 1}
- {Potential improvement 2}

---

## TESTING

### Test Coverage

**Unit Tests:**
- {Test file name} - {Coverage %}
- Key scenarios: {List}

**Integration Tests:**
- {Test file name} - {What it tests}

### Test Scenarios

**Happy Path:**
1. {Scenario description}
2. {Expected behavior}

**Error Cases:**
1. {Error scenario}
2. {Expected handling}

---

## DEPENDENCIES

### External Dependencies

**None** (or list if applicable)
- {Package name} - {Version} - {Purpose}

### Internal Dependencies

**Gateway Functions:**
- `gateway.{function}()` - {Usage}

**Other Modules:**
- `{module}.{function}()` - {Usage}

---

## CONFIGURATION

### Environment Variables

**Required:**
- `{VAR_NAME}` - {Description} - Default: {value}

**Optional:**
- `{VAR_NAME}` - {Description} - Default: {value}

### SSM Parameters

**Parameters used:**
- `/path/to/param` - {Description}

---

## DEBUGGING

### Debug Flags

**{SCOPE}_DEBUG_MODE:**
- Purpose: {What it shows}
- Output: {Sample output}

**{SCOPE}_DEBUG_TIMING:**
- Purpose: {What it measures}
- Output: {Sample output}

### Common Issues

**Issue:** {Description}
- **Symptom:** {What you see}
- **Cause:** {Why it happens}
- **Fix:** {How to resolve}

---

## CHANGELOG

### Version History

| Version | Date | Changes |
|---------|------|---------|
| {YYYY-MM-DD_1} | {Date} | Initial implementation |
| {YYYY-MM-DD_2} | {Date} | {Description of changes} |
| {YYYY-MM-DD_3} | {Date} | {Description of changes} |

### Migration Notes

**From {version} to {version}:**
- {Breaking change or important note}
- {Migration step if needed}

---

## RELATED

### Related Modules

- `{module_name}.py` - {Relationship}
- `{module_name}.py` - {Relationship}

### Related Documentation

- {NMP-ID} - {Topic}
- {LESS-ID} - {Lesson}
- {DEC-ID} - {Decision}

### Related Issues

- {BUG-ID} - {Bug description}
- {ISSUE-ID} - {Issue description}

---

**END OF FILE**

**Summary:** {One-line summary of module}
