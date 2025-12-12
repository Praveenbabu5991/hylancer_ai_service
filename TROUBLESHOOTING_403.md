# Troubleshooting 403 Forbidden Error from Project Service

## Problem
When calling AI Service endpoints that fetch categories from Project Service, getting 403 Forbidden error.

## Diagnostic Logs to Check

The AI Service now has enhanced logging. When you call the endpoint with a JWT token, you should see these logs:

### 1. AI Service Endpoint Logs
```
📨 Received Authorization header: Bearer eyJ... (length: 1274)
🔑 Extracted JWT token: eyJ... (length: 1267)
```

### 2. Service Layer Logs
```
Calling Project Service at: http://...
JWT Token present: Yes
```

### 3. HTTP Client Logs
```
🔗 Calling Project Service: http://.../api/projects/categories-and-subcategories
🔑 Authorization header present: Yes
🔑 Token format: Bearer eyJ... (length: 1274)
📥 Response status: 200 (or 403 if failing)
```

## Common Causes of 403 Error

### 1. ❌ Client Not Sending Authorization Header
**Symptoms:**
```
⚠️ No Authorization header received from client
JWT Token present: No
Authorization header present: No
```

**Solution:**
Make sure your API call includes the Authorization header:
```bash
curl -X POST http://localhost:8000/api/v1/generate_project_from_text \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"brief_description": "test", "budget": 50000}'
```

### 2. ❌ Expired JWT Token
**Symptoms:**
```
📥 Response status: 403
```

**Solution:**
Generate a fresh JWT token from your authentication system. Check the `exp` claim in your token:
```bash
# Decode token to check expiration
python3 -c "import jwt, sys; print(jwt.decode(sys.argv[1], options={'verify_signature': False}))" "YOUR_TOKEN"
```

### 3. ❌ Project Service Not Configured to Accept Tokens
**Symptoms:**
```
📥 Response status: 403
```

**Solution:**
Check your Project Service configuration:
- Is it behind API Gateway in production?
- Is it configured to accept JWT tokens?
- Does it require specific Cognito user pools?

### 4. ❌ Wrong PROJECT_SERVICE_URL
**Symptoms:**
```
Calling Project Service at: http://wrong-url
```

**Solution:**
Update `.env` file:
```
PROJECT_SERVICE_URL=http://your-actual-project-service-url
```

### 5. ❌ Network Connectivity Issues
**Symptoms:**
```
Connection error / Timeout
```

**Solution:**
- If both services are in Docker: Use service names or `host.docker.internal`
- If Project Service is external: Use full URL (http://... or https://...)

## Testing Locally vs Production

### Local Environment (Both Services on Same Machine)
```bash
# .env configuration
PROJECT_SERVICE_URL=http://host.docker.internal:8081/hylancer-project-service
```

### Production Environment (Services Behind API Gateway)
```bash
# .env configuration
PROJECT_SERVICE_URL=https://your-api-gateway-url/hylancer-project-service
```

## Verification Steps

1. **Check AI Service Logs**
```bash
docker compose logs ai_service --tail 50 | grep -E "(📨|🔑|🔗|📥)"
```

2. **Verify Token is Valid**
```bash
# The token should have these claims:
# - sub: user ID
# - email: user email
# - cognito:groups: user roles
# - exp: expiration timestamp (must be in future)
```

3. **Test Project Service Directly**
```bash
# Test if Project Service accepts the token
curl -X GET http://your-project-service/api/projects/categories-and-subcategories \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

4. **Check Response Status**
- 200: Success (check if categories are empty)
- 401: Unauthorized (no token or invalid format)
- 403: Forbidden (token rejected by Project Service)
- 404: Wrong URL
- 500: Internal server error

## Working Example

In a properly configured environment, logs should look like:

```
2025-12-12 10:25:03.041 | INFO - 📨 Received Authorization header: Bearer eyJ... (length: 1274)
2025-12-12 10:25:03.041 | INFO - 🔑 Extracted JWT token: eyJ... (length: 1267)
2025-12-12 10:25:03.042 | INFO - Calling Project Service at: http://host.docker.internal:8081/hylancer-project-service
2025-12-12 10:25:03.043 | INFO - JWT Token present: Yes
2025-12-12 10:25:03.043 | INFO - 🔗 Calling Project Service: http://...categories-and-subcategories
2025-12-12 10:25:03.044 | INFO - 🔑 Authorization header present: Yes
2025-12-12 10:25:03.044 | INFO - 🔑 Token format: Bearer eyJ... (length: 1274)
2025-12-12 10:25:03.117 | INFO - 📥 Response status: 200
```

## Contact Info

If still facing issues after checking all above, provide:
1. Complete AI Service logs (last 100 lines)
2. Project Service URL being used
3. Token expiration time (decode the JWT)
4. Whether services are behind API Gateway or direct
5. Network setup (Docker, Kubernetes, bare metal, etc.)
