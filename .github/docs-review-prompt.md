# Documentation Review Prompt

Review the ChipFlow documentation for quality, accuracy, and consistency.

## Context

ChipFlow is a platform for designing and building hardware systems (SoCs) using Python and Amaranth HDL. The documentation covers:

- **chipflow-lib**: The main Python library and CLI tool
- **amaranth**: The hardware description language
- **amaranth-soc**: System-on-Chip design library
- **chipflow-examples**: Example designs (minimal SoC, MCU SoC)

## Review Criteria

### 1. Technical Accuracy

- Do code examples actually work with the current API?
- Are command-line examples correct (`pdm chipflow ...`, etc.)?
- Are configuration file examples (`chipflow.toml`) valid?
- Do cross-references to other documentation sections resolve correctly?
- Are version numbers and URLs up to date?

### 2. Consistency

- Is terminology used consistently? (e.g., "SoC" vs "System-on-Chip", "pin" vs "port")
- Are code style conventions consistent across examples?
- Do similar concepts use similar explanations across different pages?
- Are file paths and directory structures described consistently?

### 3. Flow and Organization

- Does the getting-started guide provide a clear path for new users?
- Are prerequisites clearly stated before each section?
- Do topics build logically on each other?
- Are advanced topics appropriately separated from beginner content?
- Is the navigation structure (toctree) logical?

### 4. Completeness

- Are all major features documented?
- Are error messages and troubleshooting covered?
- Are environment variables and configuration options documented?
- Are there gaps in the examples that would confuse users?

### 5. Links and References

- Do internal cross-references (`:doc:`, `:ref:`, `:class:`) work?
- Are external URLs valid and pointing to the correct resources?
- Is the relationship between chipflow-lib, amaranth, and amaranth-soc clear?

## Output Format

Provide your findings in this structure:

```
## Summary
[Overall assessment of documentation quality - 1-2 sentences]

## Issues Found

### Critical
[Issues that would prevent users from following the documentation]

### Major
[Significant inaccuracies or confusing sections]

### Minor
[Small improvements or nitpicks]

## Recommendations
[Top 3-5 actionable improvements]

## Files Reviewed
[List of files examined]
```

If no issues are found in a category, note "None found" rather than omitting it.
