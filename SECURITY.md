# Security Documentation

## Overview

This document describes the security measures implemented in the Quizzer application to protect against common web vulnerabilities.

**Last Updated**: March 12, 2026

---

## Path Traversal Protection

### Vulnerability
Path traversal attacks allow attackers to access files outside the intended directory by using special characters like `..` in file paths.

### Mitigation
The application validates all quiz paths before loading files:

1. **Path Validation** (`quizzer/security.py`)
   - Rejects paths containing `..` (parent directory references)
   - Ensures paths end with `.json` extension
   - Resolves paths to absolute form and verifies they're within allowed directory
   - Follows and validates symbolic links

2. **Quiz ID Validation**
   - Prevents path separators (`/`, `\`) in quiz IDs used for reports
   - Blocks suspicious characters (`<`, `>`, `|`, `*`, `?`, `:`)
   - Protects against directory traversal in report file names

### Usage
```python
from quizzer.security import validate_quiz_path, validate_report_path

# Validate quiz file path
safe_path = validate_quiz_path("subfolder/quiz.json", QUIZZES_DIR)

# Validate quiz ID for reports
safe_id = validate_report_path("quiz_001")
```

### Attack Examples Blocked
- `../../../etc/passwd` → Rejected (contains `..`)
- `/etc/shadow` → Rejected (outside allowed directory)
- `folder/../quiz.json` → Rejected (contains `..`)
- `quiz.txt` → Rejected (invalid extension)
- `folder\\..\\quiz.json` → Rejected (contains `..`)

---

## Error Message Sanitization

### Vulnerability
Exposing detailed error messages can leak sensitive information about server configuration, file paths, or internal logic.

### Mitigation
- Generic error messages returned to clients
- Detailed errors logged server-side only
- Never return `str(exception)` in API responses
- Specific error types mapped to appropriate HTTP status codes

### Implementation
```python
try:
    quiz = Quiz.load(validated_path)
    return jsonify(quiz.to_dict())
except FileNotFoundError:
    # Generic client message
    return jsonify({"error": "Quiz not found"}), 404
except Exception as e:
    # Detailed  error only in logs
    logger.error(f"Error loading quiz: {e}", exc_info=True)
    # Generic client message
    return jsonify({"error": "Failed to load quiz"}), 500
```

---

## Custom Exception Hierarchy

The application uses specific exception types for better error handling:

- `QuizzerError` - Base exception for all application errors
- `InvalidQuizPathError` - Path validation failures (HTTP 400)
- `QuizNotFoundError` - Quiz file not found (HTTP 404)
- `ValidationError` - Request data validation failures (HTTP 400)
- `ReportGenerationError` - Report creation failures (HTTP 500)

See `quizzer/exceptions.py` for complete list.

---

## Input Validation

### Current Protections
- **Quiz Paths**: Validated for traversal attempts, extension, directory containment
- **Quiz IDs**: Validated for path separators and suspicious characters
- **File Extensions**: Only `.json` files accepted for quizzes

### Future Enhancements (Planned)
- Request payload validation with Pydantic schemas
- Maximum length limits for all text inputs
- Rate limiting to prevent DoS attacks
- CSRF token validation for state-changing operations

---

## Testing

The application includes comprehensive security tests in `tests/test_security.py`:

- **31 test cases** covering path validation
- Tests for common attack vectors
- Tests for edge cases (empty paths, special characters, etc.)
- Integration tests for complete attack scenarios

Run security tests:
```bash
python -m pytest tests/test_security.py -v
```

---

## Reporting Security Issues

If you discover a security vulnerability:

1. **Do NOT** open a public GitHub issue
2. Email security concerns to: [your-email@example.com]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and work with you to address the issue.

---

## Security Checklist for Contributors

Before submitting code that handles user input:

- [ ] Validate all user-provided paths using `validate_quiz_path()` or similar
- [ ] Never expose internal error details in API responses
- [ ] Use specific exception types, not generic `Exception`
- [ ] Add tests for attack vectors (path traversal, injection, etc.)
- [ ] Log detailed errors server-side with `logger.error()`
- [ ] Sanitize any data used in file operations
- [ ] Check return values and handle edge cases

---

## Security Audit History

| Date | Auditor | Scope | Findings | Status |
|------|---------|-------|----------|--------|
| 2026-03-12 | AI Code Review | Path traversal | 2 vulnerabilities | Fixed |

---

## Future Security Roadmap

See `IMPLEMENTATION_TRACKING.md` for planned security enhancements:

- Phase 1, Step 2: Error message sanitization (In Progress)
- Phase 1, Step 3: Request payload validation with Pydantic
- Phase 1, Step 4: Rate limiting implementation
- Phase 2+: Authentication, authorization, HTTPS enforcement

---

## References

- [OWASP Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
