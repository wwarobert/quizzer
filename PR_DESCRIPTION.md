# Pull Request: feat(security): Add rate limiting (Phase 1, Step 4)

**Branch**: `security/rate-limiting`
**URL**: https://github.com/wwarobert/quizzer/pull/new/security/rate-limiting

---

## Summary

This PR implements **Phase 1, Step 4** of the routes.py refactoring plan: **Rate Limiting**.

Protects the API from denial-of-service (DoS) attacks by enforcing endpoint-specific rate limits with automatic 429 responses and rate limit headers.

## Changes

### New Files
- **`tests/test_rate_limiting.py`**: 13 comprehensive tests for rate limiting configuration and enforcement

### Modified Files
- **`requirements.txt`**: Added Flask-Limiter>=3.5.0
- **`quizzer/web/app.py`**: Initialize limiter with headers enabled
- **`quizzer/web/routes.py`**: Apply rate limits to all endpoints, add RateLimitExceeded handler
- **`SECURITY.md`**: Added comprehensive rate limiting documentation
- **`IMPLEMENTATION_TRACKING.md`**: Marked Step 4 as completed

## DoS Protection

### Rate Limits by Endpoint

| Endpoint | Limit | Reason |
|----------|-------|--------|
| `/api/quizzes` | 100/hour | Quiz listing |
| `/api/quiz` | 100/hour | Quiz loading |
| `/api/check-answer` | **10/minute** | Most frequent operation |
| `/api/save-report` | 20/hour | Write operation |
| `/api/reports` | 50/hour | Report viewing |
| All others | 200/day, 50/hour | Default protection |

### Features Implemented

✅ **Per-IP tracking** (using `get_remote_address`)  
✅ **Automatic 429 responses** when limit exceeded  
✅ **Rate limit headers** in all responses:
  - `X-RateLimit-Limit` - Total allowed requests
  - `X-RateLimit-Remaining` - Remaining requests in window
  - `X-RateLimit-Reset` - Timestamp when limit resets

✅ **User-friendly error messages** for rate limit violations  
✅ **Independent counters** per endpoint (no interference between endpoints)  
✅ **In-memory storage** (suitable for single-instance deployments)  

### Attack Examples Blocked

| Attack Type | Without Rate Limiting | With Rate Limiting |
|-------------|----------------------|-------------------|
| Quiz enumeration | Unlimited requests | Max 100/hour |
| Answer brute-forcing | Unlimited attempts | Max 10/minute |
| Report generation spam | Unlimited reports | Max 20/hour |
| API resource exhaustion | Server crash | Graceful 429 response |

## Technical Implementation

### Circular Import Fix

**Problem**: routes.py importing limiter from app.py, while app.py imports register_routes from routes.py

**Solution**: Pass limiter as parameter to register_routes():

```python
# quizzer/web/app.py
limiter = Limiter(...)
limiter.init_app(app)
register_routes(app, limiter)  # Pass limiter to avoid circular import

# quizzer/web/routes.py
def register_routes(app, limiter):  # Accept limiter as parameter
    @app.route("/api/quiz")
    @limiter.limit("100 per hour")
    def get_quiz():
        ...
```

### Error Handler

Added dedicated handler for rate limit exceptions:

```python
@app.errorhandler(RateLimitExceeded)
def handle_rate_limit_exceeded(error):
    logger.warning(f"Rate limit exceeded: {request.url}")
    return jsonify({
        "error": "Rate limit exceeded",
        "message": "Too many requests. Please try again later."
    }), 429
```

### Rate Limit Headers

Enabled in limiter configuration:

```python
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    headers_enabled=True,  # Enable rate limit headers
)
```

## Production Scaling

For multi-instance deployments, switch to Redis storage:

```python
# In production environment configuration
limiter = Limiter(
    storage_uri="redis://localhost:6379",
    ...
)
```

## Testing

✅ **All 334 tests pass** (321 existing + 13 new rate limiting tests)
- 0 regressions
- 100% backward compatible
- Full coverage of rate limiting

### New Test Coverage

✅ Verify limiter is enabled and configured  
✅ Verify requests within limits succeed  
✅ Verify rate limit headers present in responses  
✅ Verify exceeded limits return 429 status code  
✅ Verify error message is user-friendly  
✅ Verify different endpoints have independent counters  
✅ Verify strict limits work correctly (10/minute for check-answer)  

### Test Examples

```python
def test_rate_limit_returns_429(self, app):
    """Rate limit exceeded should return 429 status code."""
    test_limiter = Limiter(
        key_func=get_remote_address,
        app=test_app,
        default_limits=["2 per hour"],
        storage_uri="memory://",
    )
    
    # First 2 requests succeed
    assert client.get("/test-limit").status_code == 200
    assert client.get("/test-limit").status_code == 200
    
    # Third request is rate limited
    response = client.get("/test-limit")
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json["error"]
```

## Security Impact

✅ **DoS protection**: Prevents resource exhaustion attacks  
✅ **Brute-force mitigation**: Limits answer checking attempts  
✅ **Resource fairness**: Ensures fair API access for all users  
✅ **Graceful degradation**: Returns helpful 429 responses instead of crashing  
✅ **Transparency**: Rate limit headers help clients implement backoff strategies  

## Phase 1 Complete! 🎉

With this PR, **Phase 1 (Security & Input Validation) is fully completed**:

- ✅ Step 1: Path Sanitization (Merged 2026-03-12)
- ✅ Step 2: Error Message Sanitization (Merged 2026-03-13)
- ✅ Step 3: Request Payload Validation (Merged 2026-03-13)
- ✅ Step 4: Rate Limiting (This PR - 2026-03-16)

**Next**: Phase 2 - Extract Business Logic (Service Layer)

---

## PR Checklist

- [x] All tests pass (334/334)
- [x] Rate limiting tests added (13 new tests)  
- [x] No regressions in existing functionality
- [x] Code follows Python best practices
- [x] Documentation updated (SECURITY.md)
- [x] Circular import resolved
- [x] Rate limit headers enabled
- [x] Error handler for 429 responses
- [ ] Code review completed (pending)
- [x] No breaking changes
    assert "database" not in data["error"].lower()
    assert "RuntimeError" not in data["error"]
```

## Logging Behavior

All detailed errors are logged server-side for debugging:

```python
logger.error(f"Error loading quiz {quiz_path}: {e}", exc_info=True)
# Logs full traceback and exception details
```

While clients receive sanitized messages:

```json
{"error": "Failed to load quiz"}
```

## Documentation

- Comprehensive docstrings in `error_messages.py`
- Updated `IMPLEMENTATION_TRACKING.md` with Step 2 completion
- All test functions include detailed descriptions

## CI/CD Status

Expected CI checks:
- ✅ pytest (289 tests)
- ✅ coverage (maintaining 71%+)
- ✅ black, isort, flake8, pylint
- ✅ mypy type checking
- ✅ bandit security scanning

## Breaking Changes

**None** - This is a purely additive security enhancement with full backward compatibility.

Error response structure remains identical:
```json
{"error": "message here"}
```

Only the message content is now sanitized (still user-friendly, just safer).

## Next Steps

After this PR is merged:
- Phase 1, Step 3: Add request payload validation with Pydantic
- Phase 1, Step 4: Implement rate limiting
- Phase 2: Extract business logic into services

## Review Checklist

- [x] Code follows project style guidelines
- [x] All tests pass (289/289)
- [x] No security vulnerabilities introduced
- [x] Error messages user-friendly and safe
- [x] Detailed logging preserved for debugging
- [x] Documentation is complete and accurate
- [x] Changes are backward compatible
- [x] No regressions in existing functionality

---

**Tracking**: See `IMPLEMENTATION_TRACKING.md` for full refactoring plan  
**Related**: Builds on PR #X (Path Traversal Protection)

---

## Instructions to Create PR

1. Visit: https://github.com/wwarobert/quizzer/pull/new/security/sanitize-errors
2. Copy the content above into the PR description
3. Set the title to: `feat(security): Sanitize error messages (Phase 1, Step 2)`
4. Click "Create pull request"
5. Wait for automated CI checks to complete
6. Request review from team members or use AI code review
- Python tests (pytest)
- Code coverage reporting
- Linting (black, isort, flake8, pylint)
- Type checking (mypy)
- Security scanning (bandit)
