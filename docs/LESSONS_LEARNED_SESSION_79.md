# Lessons Learned - Session 79: app/api/auth.py

**Date**: 2025-12-03  
**Module**: `app/api/auth.py`  
**Result**: TRUE 100% Coverage ✅  
**Tests**: 23 comprehensive tests

---

## 🌟 Critical Lesson: Patch at Import Location, Not Definition Location

### ⭐⭐⭐ THE MOST IMPORTANT LESSON FROM SESSION 79

**The Problem**: Tests failing because mocks weren't being used

**Initial Approach (WRONG)**:
```python
# ❌ Patching where functions are DEFINED
with patch("app.core.security.authenticate_user") as mock_auth:
    # This doesn't work when testing app/api/auth.py!
    response = client.post("/api/v1/auth/login", ...)
```

**Correct Approach**:
```python
# ✅ Patching where functions are IMPORTED
with patch("app.api.auth.authenticate_user") as mock_auth:
    # This works! Patches the imported reference
    response = client.post("/api/v1/auth/login", ...)
```

### Why This Matters

When `app/api/auth.py` does:
```python
from app.core.security import authenticate_user, create_access_token
```

It creates **local references** in the `app.api.auth` namespace. When the endpoint runs:
```python
user = authenticate_user(db, user_id, password)
```

It uses `app.api.auth.authenticate_user`, NOT `app.core.security.authenticate_user`.

### The Fix

```bash
# Replace all patch paths in test file
sed -i '' 's/patch("app\.core\.security\.authenticate_user")/patch("app.api.auth.authenticate_user")/g' tests/test_api_auth.py
sed -i '' 's/patch("app\.core\.security\.create_access_token")/patch("app.api.auth.create_access_token")/g' tests/test_api_auth.py
sed -i '' 's/patch("app\.core\.security\.get_password_hash")/patch("app.api.auth.get_password_hash")/g' tests/test_api_auth.py
```

### Impact

- **Before**: 4 failed tests, 96.12% coverage
- **After**: 0 failed tests, 100.00% coverage ✅

---

## 🎯 Lesson 1: FastAPI Dependency Override Pattern

### The Pattern

```python
@pytest.fixture
def app():
    """Create FastAPI app instance for testing"""
    from app.main import create_app
    return create_app()

@pytest.fixture
def client(app):
    """Create FastAPI test client"""
    return TestClient(app)

def test_something(app, client, mock_db):
    from app.database.config import get_primary_db_session
    
    # Override dependency
    def override_get_db():
        return mock_db
    
    app.dependency_overrides[get_primary_db_session] = override_get_db
    
    # Make request
    response = client.post("/api/v1/auth/login", ...)
    
    # Verify
    assert response.status_code == 200
    
    # IMPORTANT: Clean up!
    app.dependency_overrides.clear()
```

### Why This Works

- FastAPI's dependency injection system checks `app.dependency_overrides` first
- If a dependency is overridden, uses the override function
- If not, uses the original dependency
- Works for all `Depends()` parameters

### Common Mistake

```python
# ❌ Forgetting to clear overrides
app.dependency_overrides[get_db] = mock_get_db
# ... test ...
# app.dependency_overrides.clear()  # FORGOT THIS!

# Next test uses the mock from previous test! 💥
```

**Solution**: Always clear overrides in cleanup or use a fixture:
```python
@pytest.fixture
def app_with_mock_db(app, mock_db):
    from app.database.config import get_primary_db_session
    app.dependency_overrides[get_primary_db_session] = lambda: mock_db
    yield app
    app.dependency_overrides.clear()
```

---

## 🎯 Lesson 2: Testing FastAPI Endpoints vs Direct Function Calls

### Two Approaches

#### Approach 1: Test Via TestClient (What We Did)
```python
def test_login(app, client, mock_db):
    app.dependency_overrides[get_primary_db_session] = lambda: mock_db
    
    response = client.post("/api/v1/auth/login", json={...})
    
    assert response.status_code == 200
    assert response.json()["access_token"] == "..."
```

**Pros**:
- Tests the full HTTP layer
- Tests request parsing (JSON, Form data)
- Tests response serialization
- Tests middleware
- Integration-style testing

**Cons**:
- Requires dependency override setup
- Slightly slower
- More complex mocking

#### Approach 2: Test Functions Directly (Session 77 Style)
```python
@pytest.mark.asyncio
async def test_login():
    with patch("app.api.auth.authenticate_user") as mock_auth:
        mock_auth.return_value = user
        
        result = await login(request, mock_db)
        
        assert result.access_token == "..."
```

**Pros**:
- Simpler mocking
- Faster execution
- Direct function testing

**Cons**:
- Doesn't test HTTP layer
- Doesn't test request parsing
- Must handle async if endpoints are async

### When to Use Each

- **TestClient**: When testing API contracts, HTTP behavior, authentication
- **Direct Calls**: When testing internal logic, helper functions, calculations

**Session 79 Choice**: TestClient (better for API endpoint testing)

---

## 🎯 Lesson 3: Mock Database Query Chains

### The Pattern

```python
# Setup query chain
mock_db.query.return_value.filter.return_value.first.return_value = user

# This allows:
result = db.query(SimpleUser).filter(SimpleUser.user_id == "test").first()
# result == user
```

### Multiple Results vs Single Result

```python
# Single result (first())
mock_db.query.return_value.filter.return_value.first.return_value = user

# Multiple results (all())
mock_db.query.return_value.filter.return_value.all.return_value = [user1, user2]
```

### Testing "Not Found" Scenarios

```python
# No user found
mock_db.query.return_value.filter.return_value.first.return_value = None

# Then test should expect 404 or error response
```

---

## 🎯 Lesson 4: Tracking Objects Added to Mocks

### The Problem

When testing registration, we need to verify the user object that was added:
```python
mock_db.add(user)  # How do we check what user was?
```

### The Solution

```python
added_user = None

def mock_add(user):
    nonlocal added_user
    added_user = user
    # Set attributes that would be set by DB
    user.id = 1
    user.ui_language = "en"

mock_db.add.side_effect = mock_add

# ... make request ...

# Verify what was added
assert added_user is not None
assert added_user.user_id == "expected_id"
assert added_user.role == UserRole.PARENT
```

### Why Use `nonlocal`

```python
# ❌ Without nonlocal (doesn't work)
added_user = None

def mock_add(user):
    added_user = user  # Creates NEW local variable!

# ✅ With nonlocal (works)
added_user = None

def mock_add(user):
    nonlocal added_user  # Uses outer scope variable
    added_user = user
```

---

## 🎯 Lesson 5: Form Data vs JSON in FastAPI

### JSON Request Body

```python
# Endpoint uses Pydantic model
@router.post("/login")
async def login(request: LoginRequest):
    ...

# Test sends JSON
response = client.post("/api/v1/auth/login", json={
    "user_id": "test",
    "password": "pass123"
})
```

### Form Data

```python
# Endpoint uses Form() parameters
@router.put("/profile")
async def update_profile(
    username: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
):
    ...

# Test sends form data
response = client.put("/api/v1/auth/profile", data={
    "username": "new_name",
    "email": "new@example.com"
})
```

### Common Mistake

```python
# ❌ Using JSON for Form endpoint
response = client.put("/api/v1/auth/profile", json={...})
# 422 Unprocessable Entity

# ✅ Using data for Form endpoint
response = client.put("/api/v1/auth/profile", data={...})
```

---

## 🎯 Lesson 6: Testing Null/None Edge Cases

### The Importance

Database columns can be nullable. Test what happens when they are!

### Pattern

```python
def test_with_null_role(app, client, sample_user):
    # Set role to None
    sample_user.role = None
    
    # Override auth
    app.dependency_overrides[require_auth] = lambda: sample_user
    
    # Make request
    response = client.get("/api/v1/auth/profile")
    
    # Verify default handling
    assert response.json()["role"] == "child"
```

### Places to Test Null Values

1. **Optional Fields**: email, first_name, last_name
2. **Enum Fields**: role (might be None in DB)
3. **Timestamps**: updated_at, last_login before first use
4. **Relationships**: Foreign keys that might be null

### Code Pattern for Null Handling

```python
# In endpoint
role=current_user.role.value if current_user.role else "child"
```

---

## 🎯 Lesson 7: Permission Testing Boundaries

### Test All Permission Levels

For an endpoint that checks permissions:
```python
if current_user.role not in [UserRole.PARENT, UserRole.ADMIN]:
    raise HTTPException(status_code=403, detail="Insufficient permissions")
```

**Must Test**:
1. ✅ Child role (should be forbidden - 403)
2. ✅ Parent role (should be allowed - 200)
3. ✅ Admin role (should be allowed - 200)

### Don't Just Test Success

```python
# ❌ Only testing success case
def test_list_users(app, client, parent_user):
    app.dependency_overrides[require_auth] = lambda: parent_user
    response = client.get("/api/v1/auth/users")
    assert response.status_code == 200

# ✅ Also test failure cases
def test_list_users_forbidden(app, client, child_user):
    app.dependency_overrides[require_auth] = lambda: child_user
    response = client.get("/api/v1/auth/users")
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["detail"]
```

---

## 🎯 Lesson 8: Conditional Update Testing

### The Challenge

Endpoint that updates only provided fields:
```python
if username:
    current_user.username = username
if email:
    current_user.email = email
# ... more fields ...
```

### Test Coverage Required

1. **All fields provided**
2. **Some fields provided** (partial update)
3. **No fields provided** (still updates timestamp)

### Example

```python
def test_update_all_fields(app, client, mock_db, user):
    response = client.put("/api/v1/auth/profile", data={
        "username": "new_name",
        "email": "new@example.com",
        "first_name": "New",
        "last_name": "Name",
        "ui_language": "es"
    })
    # Verify all updated
    assert user.username == "new_name"
    assert user.email == "new@example.com"

def test_update_partial_fields(app, client, mock_db, user):
    original_email = user.email
    response = client.put("/api/v1/auth/profile", data={
        "username": "new_name"
    })
    # Verify only username updated
    assert user.username == "new_name"
    assert user.email == original_email  # Unchanged

def test_update_no_fields(app, client, mock_db, user):
    response = client.put("/api/v1/auth/profile", data={})
    # Timestamp still updated
    assert user.updated_at is not None
```

---

## 🎯 Lesson 9: Testing Response Structure

### Verify Complete Response Schema

```python
response = client.post("/api/v1/auth/login", json={...})

# ✅ Don't just check status code
assert response.status_code == 200

# ✅ Verify complete response structure
data = response.json()
assert "access_token" in data
assert "token_type" in data
assert data["token_type"] == "bearer"
assert "user" in data
assert data["user"]["user_id"] == "testuser123"
assert data["user"]["username"] == "Test User"
assert data["user"]["role"] == "child"
# ... verify all expected fields ...
```

### Why This Matters

- Catches missing fields
- Catches wrong field names
- Catches wrong data types
- Documents expected API contract

---

## 🎯 Lesson 10: Test Organization

### Class-Based Organization by Endpoint and Scenario

```python
class TestLoginSuccess:
    """Test successful login scenarios"""
    def test_valid_credentials(self): ...
    def test_no_password(self): ...
    def test_null_role(self): ...

class TestLoginFailure:
    """Test failed login scenarios"""
    def test_invalid_credentials(self): ...
    def test_nonexistent_user(self): ...
```

### Benefits

1. **Clear Structure**: Easy to find tests
2. **Logical Grouping**: Related tests together
3. **Shared Setup**: Can use class-level fixtures
4. **Documentation**: Class docstrings explain test scope

### Naming Convention

- `TestEndpointSuccess` - Happy path scenarios
- `TestEndpointFailure` - Error scenarios
- `TestEndpointEdgeCases` - Null values, boundary conditions

---

## 🎯 Lesson 11: Debugging FastAPI Tests

### Common Issues and Solutions

#### Issue 1: Dependency Override Not Working
```python
# ❌ Wrong
app.dependency_overrides[get_db] = mock_db

# ✅ Correct
app.dependency_overrides[get_db] = lambda: mock_db
```

#### Issue 2: Mock Not Being Used
```python
# ❌ Patching at definition location
patch("app.core.security.authenticate_user")

# ✅ Patching at import location
patch("app.api.auth.authenticate_user")
```

#### Issue 3: 401 Unauthorized on Protected Endpoints
```python
# ❌ Forgetting to override auth
response = client.get("/api/v1/auth/profile")

# ✅ Override auth dependency
from app.core.security import require_auth
app.dependency_overrides[require_auth] = lambda: sample_user
response = client.get("/api/v1/auth/profile")
```

#### Issue 4: Form Data vs JSON Mismatch
```python
# ❌ Using json for Form endpoint
response = client.put("/api/v1/auth/profile", json={...})

# ✅ Using data for Form endpoint
response = client.put("/api/v1/auth/profile", data={...})
```

---

## 📚 Patterns Library

### Pattern 1: Basic Endpoint Test with Mocks

```python
def test_endpoint(app, client, mock_db):
    from app.database.config import get_primary_db_session
    from app.core.security import require_auth
    
    # Override dependencies
    app.dependency_overrides[get_primary_db_session] = lambda: mock_db
    app.dependency_overrides[require_auth] = lambda: sample_user
    
    # Patch imported functions
    with patch("app.api.auth.some_function") as mock_func:
        mock_func.return_value = expected_value
        
        # Make request
        response = client.post("/api/v1/endpoint", json={...})
        
        # Verify
        assert response.status_code == 200
        assert response.json() == {...}
    
    # Cleanup
    app.dependency_overrides.clear()
```

### Pattern 2: Testing Error Responses

```python
def test_error_case(app, client):
    # Setup condition that causes error
    app.dependency_overrides[some_dependency] = lambda: None
    
    # Make request
    response = client.post("/api/v1/endpoint", json={...})
    
    # Verify error response
    assert response.status_code == 400  # or 401, 403, 404, etc.
    assert "expected error message" in response.json()["detail"]
    
    app.dependency_overrides.clear()
```

### Pattern 3: Tracking Database Operations

```python
def test_database_operation(app, client, mock_db):
    captured_object = None
    
    def capture_add(obj):
        nonlocal captured_object
        captured_object = obj
        obj.id = 1  # Simulate DB setting ID
    
    mock_db.add.side_effect = capture_add
    
    # Make request that adds to DB
    response = client.post("/api/v1/endpoint", json={...})
    
    # Verify what was added
    assert captured_object is not None
    assert captured_object.field == "expected_value"
    mock_db.commit.assert_called_once()
```

---

## 💡 Key Takeaways for Future API Testing

### Critical Rules

1. **Patch at import location**, not definition location
2. **Always clean up** `app.dependency_overrides`
3. **Test all permission levels** (allowed and forbidden)
4. **Test null/None values** for all nullable fields
5. **Use `data={}` for Form**, `json={}` for request bodies
6. **Verify complete response structure**, not just status codes
7. **Test conditional updates** with all/some/no fields
8. **Track database operations** with `nonlocal` and `side_effect`

### Test Coverage Checklist

For each endpoint, ensure tests for:
- ✅ Success case (200/201)
- ✅ Error cases (400/401/403/404/500)
- ✅ Edge cases (null values, empty data)
- ✅ Permission boundaries (if applicable)
- ✅ Database operations (add/update/delete)
- ✅ Complete response structure

---

## 🌟 Session 79 Success Factors

1. **Systematic Debugging**: Identified root cause through iteration
2. **Pattern Recognition**: Applied Session 77's API testing learnings
3. **Thorough Testing**: 23 tests covering all scenarios
4. **Zero Compromises**: TRUE 100% with all branches covered
5. **Documentation**: Complete lessons captured for future reference

**Result**: 47th module at TRUE 100% coverage! 🎊
