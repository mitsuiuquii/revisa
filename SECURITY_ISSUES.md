# REVISA - Security Issues Report

## Identified Security Vulnerabilities

### 1. ✅ PARTIALLY FIXED: Admin Password Hardcoding
**Severity**: CRITICAL  
**Status**: PARTIAL FIX

**Issue**: 
- Frontend had hardcoded admin password as string constant
- Password was hardcoded in backend environment fallback
- User input was ignored on login

**Fixed**:
- ✅ Frontend: Removed hardcoded password constant
- ✅ Frontend: Now uses actual user input from password field
- ⏳ Backend: Still has fallback password in `os.environ.get('ADMIN_SECRET', 'revisa@admin2025')`

**Remaining Work**:
- Backend: Remove hardcoded fallback password
- Backend: Require ADMIN_SECRET environment variable
- Add rate limiting for admin login attempts
- Add logging for admin access attempts

**Recommended Fix**:
```python
# In server.py, change:
# FROM:
ADMIN_SECRET = os.environ.get('ADMIN_SECRET', 'revisa@admin2025')

# TO:
ADMIN_SECRET = os.environ.get('ADMIN_SECRET')
if not ADMIN_SECRET:
    raise ValueError("ADMIN_SECRET environment variable must be set")
```

---

### 2. ⏳ NOT FIXED: Destructive Database Re-seed on Startup
**Severity**: CRITICAL  
**Status**: NOT FIXED

**Issue**:
- Backend startup event checks if subjects/lessons match seed data
- If mismatch detected, it deletes ALL existing data
- No backup or recovery mechanism
- Can cause data loss in production if environment changes

**Location**: `backend/server.py` - startup event

**Recommended Fix**:
- Add migration system instead of destructive deletes
- Create versioned seed data
- Add confirmation prompt for data destructive operations
- Add audit logging for deletions
- Separate seed operation from startup

---

### 3. ⏳ NOT FIXED: Token Storage in localStorage
**Severity**: HIGH  
**Status**: NOT FIXED

**Issue**:
- JWT tokens stored in localStorage
- Vulnerable to XSS attacks
- Any injected JavaScript can steal tokens
- No token expiration validation on frontend

**Location**: `frontend/src/lib/auth.jsx`, `api.js`

**Recommended Fix**:
- Move token to httpOnly cookie (more secure)
- Implement token refresh mechanism
- Add XSS protection headers to backend
- Validate token expiration on frontend
- Implement logout that clears all stored data

```javascript
// Better approach:
// Store in sessionStorage (cleared on browser close) or
// Use httpOnly cookies with proper CSRF protection
```

---

### 4. ⏳ NOT FIXED: Permissive CORS Configuration
**Severity**: HIGH  
**Status**: NOT FIXED

**Issue**:
- CORS allows all origins with `*`
- Credentials are included with CORS requests
- No origin whitelist
- No preflight validation

**Location**: `backend/server.py` - CORS middleware

**Recommended Fix**:
```python
# Change from:
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True)

# To:
allowed_origins = [
    "http://localhost:3000",
    "https://revisa.app",
]
app.add_middleware(CORSMiddleware, 
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 5. ⏳ NOT FIXED: Secrets Logged to Console
**Severity**: MEDIUM  
**Status**: NOT FIXED

**Issue**:
- JWT tokens logged in console (admin login)
- Session IDs logged in Google auth callback
- Secret parts of tokens exposed in logs
- No log filtering or redaction

**Location**: 
- `frontend/src/pages/Admin.jsx` - lines 38-45
- `frontend/src/pages/AuthCallback.jsx` - lines 24

**Recommended Fix**:
```javascript
// Remove or redact logging:
// DON'T log full tokens
console.log("✅ Login bem-sucedido");  // Remove detailed token logging

// Better:
console.log("✅ Auth successful - token received");
```

---

### 6. ⏳ NOT FIXED: No Rate Limiting
**Severity**: MEDIUM  
**Status**: NOT FIXED

**Issue**:
- No rate limiting on login endpoints
- No rate limiting on API endpoints
- Vulnerable to brute force attacks
- Vulnerable to DDoS attacks

**Recommended Fix**:
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/auth/login")
@limiter.limit("5/minute")  # 5 attempts per minute
async def login(request: Request, credentials: LoginRequest):
    ...
```

---

### 7. ⏳ NOT FIXED: No HTTPS Enforcement
**Severity**: HIGH (Production)  
**Status**: N/A (Local Dev)

**Issue**:
- No HTTPS redirect
- No HSTS headers
- Credentials sent over potential HTTP
- API keys exposed in transit

**Recommended Fix**:
- Enable HTTPS in production
- Add HSTS header with long max-age
- Redirect HTTP to HTTPS

---

### 8. ⏳ NOT FIXED: No Input Validation
**Severity**: MEDIUM  
**Status**: NOT FIXED

**Issue**:
- User inputs not properly validated
- Potential SQL injection (via MongoDB)
- No length restrictions on some fields
- No type validation

**Recommended Fix**:
- Use Pydantic models with validation
- Sanitize all user inputs
- Add input length limits
- Validate email format
- Validate password strength

---

### 9. ⏳ NOT FIXED: No Authentication on Sensitive Endpoints
**Severity**: HIGH  
**Status**: NOT FIXED

**Issue**:
- Some endpoints might not check authentication
- Admin endpoints should have additional verification
- No endpoint access logging

**Recommended Audit**:
- Review all endpoints for auth checks
- Add comprehensive access logging
- Implement permission-based access control

---

## Priority Fixes

### Phase 3 - CRITICAL (Do First):
1. Remove hardcoded admin password from backend
2. Implement proper token storage (httpOnly cookies)
3. Fix CORS configuration with whitelist
4. Add rate limiting

### Phase 4 - HIGH:
1. Implement logging redaction
2. Add HTTPS enforcement (production)
3. Add comprehensive input validation
4. Audit all endpoint security

### Phase 5 - MEDIUM:
1. Implement token refresh mechanism
2. Add CSRF protection
3. Create security audit trail
4. Implement 2FA for admin

---

## Testing Recommendations

### Security Tests to Add:
- [ ] Test brute force protection
- [ ] Test XSS prevention
- [ ] Test CORS restrictions
- [ ] Test token expiration
- [ ] Test SQL/NoSQL injection prevention
- [ ] Test rate limiting
- [ ] Audit console logs for sensitive data

### Recommended Tools:
- OWASP ZAP for scanning
- Burp Suite for penetration testing
- npm audit for dependency vulnerabilities
- SonarQube for code quality

---

**Last Updated**: 2024
**Status**: Phase 2 (Visual Design) Complete - Security Fixes Pending
