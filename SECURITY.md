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

## Request Payload Validation

### Vulnerability
Invalid or malicious request data can cause errors, crashes, or unexpected behavior.

### Mitigation
All incoming request data is validated using Pydantic schemas before processing:

1. **Schema Validation** (`quizzer/web/schemas.py`)
   - Required field validation
   - Data type validation (strings, integers, floats, booleans)
   - Length limits (max 10k characters for text fields)
   - Range validation (no negative values where inappropriate)
   - Cross-field validation (e.g., correct_count ≤ total_questions)

2. **Validation Behavior**
   - Returns `400 Bad Request` for invalid payloads
   - Detailed validation errors logged server-side only
   - Extra fields rejected (`extra='forbid'`)

### Implementation
```python
from quizzer.web.schemas import CheckAnswerRequest

try:
    data = CheckAnswerRequest(**request.json)
    # Validated data is safe to use
except ValidationError as e:
    logger.warning(f"Invalid request payload: {e}")
    return jsonify({"error": "Invalid request data"}), 400
```

---

## Rate Limiting (DoS Protection)

### Vulnerability
Without rate limiting, attackers can overwhelm the server with excessive requests, causing denial of service or resource exhaustion.

### Mitigation
Flask-Limiter is configured to limit requests per endpoint:

**Rate Limits by Endpoint:**
- `/api/quizzes` - **100 per hour** (listing quizzes)
- `/api/quiz` - **100 per hour** (loading quiz data)
- `/api/check-answer` - **10 per minute** (answer checking, most frequent)
- `/api/save-report` - **20 per hour** (saving reports)
- `/api/reports` - **50 per hour** (viewing reports)
- **Default limits**: 200 per day, 50 per hour (all other endpoints)

### Features
1. **Per-IP Tracking**: Rate limits are tracked by client IP address
2. **Automatic 429 Responses**: Exceeded limits return `429 Too Many Requests`
3. **Rate Limit Headers**: Responses include:
   - `X-RateLimit-Limit` - Total allowed requests
   - `X-RateLimit-Remaining` - Remaining requests in window
   - `X-RateLimit-Reset` - Time when limit resets
4. **In-Memory Storage**: Uses memory-based storage (suitable for single-instance deployments)

### Configuration
```python
# quizzer/web/app.py
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    headers_enabled=True,
)
```

### Production Scaling
For multi-instance deployments, configure Redis storage:
```python
storage_uri="redis://localhost:6379"
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
- **Request Payloads**: Validated with Pydantic schemas (required fields, types, lengths, ranges)
- **Rate Limiting**: Per-endpoint limits to prevent DoS attacks

### Future Enhancements (Planned)
- CSRF token validation for state-changing operations
- Input sanitization for HTML/JavaScript injection prevention
- File upload validation (if file upload feature added)

---

## Testing
:

- **tests/test_security.py**: 31 test cases for path validation
- **tests/test_error_messages.py**: 17 tests for error sanitization
- **tests/test_payload_validation.py**: 32 tests for request validation
- **tests/test_rate_limiting.py**: 13 tests for DoS protection

Run all security tests:
```bash
python -m pytest tests/test_security.py tests/test_error_messages.py tests/test_payload_validation.py tests/test_rate_limiting
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
| 2026-03-12 | AI Code Review | Path traversal | 2 vulnerabilities | ✅ Fixed |
| 2026-03-13 | AI Code Review | Error message leakage | Multiple endpoints | ✅ Fixed |
| 2026-03-13 | AI Code Review | Missing input validation | POST endpoints | ✅ Fixed |
| 2026-03-16 | AI Code Review | DoS vulnerability | No rate limiting | ✅ Fixed |

---
**Phase 1: Security & Input Validation** (✅ COMPLETED)
- ✅ Step 1: Path sanitization (Completed 2026-03-12)
- ✅ Step 2: Error message sanitization (Completed 2026-03-13)
- ✅ Step 3: Request payload validation with Pydantic (Completed 2026-03-13)
- ✅ Step 4: Rate limiting implementation (Completed 2026-03-16)

**Phase 2+: Advanced Security** (Planned)
- Authentication and authorization
- HTTPS enforcement
- Content Security Policy headers
- Session management and CSRF protection

See `IMPLEMENTATION_TRACKING.md` for complete roadmap.
- Phase 1, Step 3: Request payload validation with Pydantic
- Phase 1, Step 4: Rate limiting implementation
- Phase 2+: Authentication, authorization, HTTPS enforcement

---

## References

- [OWASP Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
