# AI Language Tutor App - Code Style Guide

**Version**: 1.0  
**Date**: 2025-10-06  
**Status**: OFFICIAL - Mandatory for all contributions  
**Last Updated**: Phase 4.2.6 Phase 2B

---

## Table of Contents

1. [Introduction](#introduction)
2. [Python Style Fundamentals](#python-style-fundamentals)
3. [Import Organization](#import-organization)
4. [Framework-Specific Patterns](#framework-specific-patterns)
5. [Code Complexity Guidelines](#code-complexity-guidelines)
6. [Error Handling](#error-handling)
7. [Type Hints and Validation](#type-hints-and-validation)
8. [Database and Persistence](#database-and-persistence)
9. [Testing Standards](#testing-standards)
10. [Documentation Requirements](#documentation-requirements)
11. [Linting and Tools](#linting-and-tools)

---

## Introduction

This guide defines the official code style for the AI Language Tutor App. It consolidates decisions made throughout Phase 4.2.6 comprehensive codebase audit.

### Philosophy

1. **Readability First**: Code is read 10x more than written
2. **Consistency Over Preference**: Follow established patterns
3. **Explicit Over Implicit**: Clear intent beats clever tricks
4. **Type Safety**: Use type hints everywhere
5. **Test Coverage**: 100% for critical paths

### Scope

- **Required**: All new code MUST follow this guide
- **Existing Code**: Refactor when touching files
- **Exceptions**: Must be documented with `# noqa: CODE - justification`

---

## Python Style Fundamentals

### Base Standard: PEP 8 + Black

We follow [PEP 8](https://peps.python.org/pep-0008/) with [Black](https://black.readthedocs.io/) formatting.

**Line Length**: 88 characters (Black default)

**Indentation**: 4 spaces (no tabs)

**String Quotes**: Double quotes `"` for strings, single quotes `'` for dict keys when convenient

```python
# ✅ GOOD
message = "Hello, world!"
config = {"key": "value"}

# ❌ BAD (inconsistent)
message = 'Hello, world!'
config = {'key': 'value'}
```

### Whitespace and Formatting

**Trailing Whitespace**: Never allowed

```python
# ✅ GOOD
def calculate(x: int) -> int:
    return x * 2

# ❌ BAD (trailing whitespace)
def calculate(x: int) -> int:░░
    return x * 2░
```

**Blank Lines**:
- 2 blank lines between top-level functions/classes
- 1 blank line between methods
- 1 blank line at end of file

```python
# ✅ GOOD
class User:
    def __init__(self):
        pass

    def save(self):
        pass


class Admin(User):
    pass

# File ends with newline ↓
```

### F-strings vs String Formatting

**Use f-strings** when you have variables to interpolate:

```python
# ✅ GOOD
name = "Alice"
message = f"Hello, {name}!"

# ❌ BAD (unnecessary f-string)
message = f"Hello, world!"  # No variables

# ✅ CORRECT
message = "Hello, world!"
```

**Don't use f-strings without placeholders** (Phase 2B: 48 issues fixed)

### Boolean Comparisons

**Use `is` for `True`/`False`/`None` comparisons**:

```python
# ✅ GOOD
if value is True:
if flag is False:
if result is None:
if active:  # Direct boolean check

# ❌ BAD
if value == True:
if flag == False:
if result == None:
```

**Phase 2B: 35 issues fixed**

### Variable Naming

**Intentional Placeholders**: Use underscore prefix + noqa when needed

```python
# ✅ GOOD (intentional placeholder with justification)
_response = api.call()  # noqa: F841 - response needed for debugging context

# ❌ BAD (unused without justification)
response = api.call()  # F841: unused variable
```

**Phase 2B: 23 issues suppressed with proper justification**

---

## Import Organization

### Standard Order

Imports must follow this order (enforced by `isort`):

1. **Standard library** imports
2. **Third-party** imports
3. **Local application** imports

```python
# ✅ GOOD
import os
import sys
from datetime import datetime
from typing import List, Dict

import fastapi
from pydantic import BaseModel
from sqlalchemy import Column

from app.models.user import User
from app.services.ai_router import AIRouter
```

### Star Imports

**FORBIDDEN** in all code except FastHTML frontend files:

```python
# ✅ ALLOWED ONLY in app/frontend/*.py
from fasthtml.common import *

# ❌ FORBIDDEN everywhere else
from anthropic import *  # Never do this
from typing import *     # Never do this
```

**Reason**: See `docs/FASTHTML_PATTERN_JUSTIFICATION.md`

**Phase 2B: 2,163 FastHTML star imports documented and approved**

### Import After Modifications

When imports must come after `sys.path`, logger config, etc., **document with noqa**:

```python
# ✅ GOOD
import sys
sys.path.insert(0, ".")

from app.models import User  # noqa: E402 - Required after sys.path modification
```

**Phase 2B: 37 import order issues documented**

---

## Framework-Specific Patterns

### FastHTML Frontend

**Star Imports**: Required pattern for FastHTML

```python
from fasthtml.common import *

def user_dashboard():
    return Div(
        H1("Dashboard"),
        P("Welcome back!"),
        Button("Continue Learning")
    )
```

**Component Composition**: Use FastHTML's Pythonic HTML

```python
# ✅ GOOD - Pythonic, readable
Card(
    H2("Profile"),
    P("User information"),
    Button("Edit", cls="btn-primary")
)

# ❌ BAD - HTML strings
"""
<div class="card">
    <h2>Profile</h2>
    <p>User information</p>
    <button class="btn-primary">Edit</button>
</div>
"""
```

### FastAPI Backend

**Dependency Injection**: Use FastAPI's DI pattern

```python
# ✅ GOOD
from fastapi import Depends
from app.database.config import get_db

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# ❌ BAD - Direct DB access
@app.get("/users")
def get_users():
    db = SessionLocal()  # Don't create sessions manually
    return db.query(User).all()
```

**Response Models**: Always specify with Pydantic

```python
# ✅ GOOD
@app.get("/users/{id}", response_model=UserResponse)
def get_user(id: int):
    ...

# ❌ BAD - No type safety
@app.get("/users/{id}")
def get_user(id: int):
    ...
```

### Pydantic V2

**Use V2 patterns** (migrated from V1 in Phase 2):

```python
# ✅ GOOD - Pydantic V2
from pydantic import BaseModel, field_validator, Field

class User(BaseModel):
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        return v.lower()

# ❌ BAD - Pydantic V1 (deprecated)
class User(BaseModel):
    email: str = Field(..., regex=r"...")  # regex → pattern
    
    @validator("email")  # validator → field_validator
    def validate_email(cls, v):
        return v.lower()
```

**Phase 2: 38 Pydantic V1→V2 migrations completed**

---

## Code Complexity Guidelines

### Complexity Limits

**Cyclomatic Complexity** (measured by `radon`):

| Level | Range | Status | Action |
|-------|-------|--------|--------|
| **A** | 1-5 | ✅ Ideal | Target for all new code |
| **B** | 6-10 | ✅ Good | Acceptable, monitor growth |
| **C** | 11-20 | ⚠️ Moderate | Document, plan refactoring |
| **D** | 21-30 | 🔴 High | Refactor required |
| **E** | 31-40 | 🔴 Very High | Urgent refactoring |
| **F** | 41+ | 🔴 Critical | Immediate refactoring |

**Current State** (Phase 2B):
- **C-level**: 41 functions documented (see `docs/COMPLEXITY_C_FUNCTIONS_DOCUMENTATION.md`)
- **D-level**: 8 functions (refactoring in Phase 2B subtasks 2b_11-2b_16)
- **E-level**: 2 functions (refactoring in Phase 2B subtasks 2b_11-2b_12)

### Complexity Reduction Strategies

**1. Extract Helper Functions**

```python
# ❌ BAD - Complexity: 15
def process_order(order):
    # Validation (5 branches)
    # Processing (6 branches)
    # Notification (4 branches)

# ✅ GOOD - Complexity: 5 each
def process_order(order):
    validate_order(order)
    execute_order(order)
    notify_customer(order)
```

**2. Early Returns**

```python
# ❌ BAD - Nested ifs
def check_permission(user, resource):
    if user:
        if user.is_active:
            if user.has_role("admin"):
                return True
    return False

# ✅ GOOD - Early returns
def check_permission(user, resource):
    if not user:
        return False
    if not user.is_active:
        return False
    return user.has_role("admin")
```

**3. Strategy Pattern for Conditionals**

```python
# ❌ BAD - Many if/elif
def get_provider(type):
    if type == "claude":
        return ClaudeService()
    elif type == "mistral":
        return MistralService()
    elif type == "qwen":
        return QwenService()
    # ... 10 more

# ✅ GOOD - Registry pattern
PROVIDERS = {
    "claude": ClaudeService,
    "mistral": MistralService,
    "qwen": QwenService,
}

def get_provider(type):
    return PROVIDERS[type]()
```

---

## Error Handling

### Exception Specificity

**ALWAYS use specific exceptions** - never bare `except:`:

```python
# ✅ GOOD - Specific exceptions
try:
    data = json.loads(response)
except (json.JSONDecodeError, TypeError, ValueError) as e:
    logger.error(f"JSON parsing failed: {e}")
    return None

# ❌ BAD - Bare except
try:
    data = json.loads(response)
except:  # F722: bare except clause
    return None
```

**Phase 2B: 12 bare except clauses fixed with context-aware exception types**

### Exception Hierarchy

```python
# ✅ GOOD - Most specific first
try:
    result = operation()
except ValueError:
    handle_value_error()
except TypeError:
    handle_type_error()
except Exception as e:
    handle_generic_error(e)

# ❌ BAD - Generic first (unreachable code)
try:
    result = operation()
except Exception as e:  # Catches everything
    handle_generic_error(e)
except ValueError:  # Never reached
    handle_value_error()
```

### Logging Errors

**Always log with context**:

```python
# ✅ GOOD
try:
    user = get_user(user_id)
except UserNotFoundError as e:
    logger.error(f"User lookup failed: user_id={user_id}, error={e}")
    raise

# ❌ BAD - No context
try:
    user = get_user(user_id)
except UserNotFoundError:
    logger.error("Error")  # What error? Which user?
    raise
```

---

## Type Hints and Validation

### Type Hints Required

**All functions must have type hints**:

```python
# ✅ GOOD
def calculate_score(
    user_id: int,
    answers: List[str],
    max_score: float = 100.0
) -> Dict[str, Any]:
    ...

# ❌ BAD - No type hints
def calculate_score(user_id, answers, max_score=100.0):
    ...
```

### Optional and Union Types

```python
from typing import Optional, Union

# ✅ GOOD - Python 3.10+ union syntax
def get_user(user_id: int) -> User | None:
    ...

# ✅ ALSO GOOD - Traditional Optional
def get_user(user_id: int) -> Optional[User]:
    ...

# ✅ GOOD - Multiple types
def process(data: str | bytes | Path) -> bool:
    ...
```

### Generic Types

```python
from typing import List, Dict, TypeVar

T = TypeVar("T")

# ✅ GOOD
def first_or_none(items: List[T]) -> T | None:
    return items[0] if items else None

# ❌ BAD - No generic
def first_or_none(items: List) -> Any:
    return items[0] if items else None
```

---

## Database and Persistence

### DateTime Handling

**Python 3.12+ compatible** (Phase 0 fix):

```python
# ✅ GOOD - Python 3.12+
from datetime import datetime, timezone

now = datetime.now(timezone.utc)

# ❌ BAD - Deprecated in Python 3.12
now = datetime.utcnow()  # DeprecationWarning
```

**Phase 0: 28 datetime.utcnow() → datetime.now(timezone.utc) migrations**

### SQLAlchemy 2.0

**Use modern import paths**:

```python
# ✅ GOOD - SQLAlchemy 2.0
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# ❌ BAD - Deprecated
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
```

**Phase 1: Import path updated**

### Session Management

**Always use context managers**:

```python
# ✅ GOOD
from app.database.config import get_db

with get_db() as db:
    user = db.query(User).first()

# ❌ BAD - Manual session management
db = SessionLocal()
user = db.query(User).first()
db.close()  # Easy to forget
```

---

## Testing Standards

### Test Organization

```python
# ✅ GOOD - Descriptive test names
def test_user_creation_with_valid_email_succeeds():
    user = User(email="test@example.com")
    assert user.email == "test@example.com"

def test_user_creation_with_invalid_email_raises_validation_error():
    with pytest.raises(ValidationError):
        User(email="invalid")

# ❌ BAD - Vague names
def test_user():
    ...

def test_user_2():
    ...
```

### Fixtures

**Use pytest fixtures** for reusable test data:

```python
import pytest

@pytest.fixture
def sample_user():
    return User(
        username="testuser",
        email="test@example.com"
    )

def test_user_authentication(sample_user):
    assert sample_user.authenticate("password")
```

### Validation Requirements

**Phase 2B quality gates require**:
1. ✅ Environment validation (5/5 checks)
2. ✅ Static analysis (100% success)
3. ✅ Integration tests (8/8 passing)
4. ✅ Evidence artifacts generated
5. ✅ No regressions

---

## Documentation Requirements

### Docstrings

**Required for all public functions/classes**:

```python
# ✅ GOOD
def calculate_retention_rate(
    user_id: int,
    start_date: datetime,
    end_date: datetime
) -> float:
    """
    Calculate memory retention rate for a user over a period.
    
    Args:
        user_id: The user's database ID
        start_date: Period start (inclusive)
        end_date: Period end (inclusive)
    
    Returns:
        Retention rate as percentage (0-100)
    
    Raises:
        UserNotFoundError: If user_id doesn't exist
        ValueError: If end_date < start_date
    """
    ...

# ❌ BAD - No docstring
def calculate_retention_rate(user_id, start_date, end_date):
    ...
```

### Inline Comments

**Use for complex logic only**:

```python
# ✅ GOOD - Explains WHY
# Use exponential backoff to avoid overwhelming the API
# during temporary outages (max 3 retries, 2^n seconds)
for attempt in range(3):
    try:
        return api.call()
    except RateLimitError:
        time.sleep(2 ** attempt)

# ❌ BAD - Explains WHAT (code is self-explanatory)
# Loop 3 times
for attempt in range(3):
    ...
```

### Suppression Comments

**Always justify linting suppressions**:

```python
# ✅ GOOD
from fasthtml.common import *  # noqa: F403 - FastHTML framework pattern

# ❌ BAD
from fasthtml.common import *  # noqa: F403
```

---

## Linting and Tools

### Required Tools

**Pre-commit hooks** (`.git/hooks/pre-commit`):
1. **Black**: Auto-formatting
2. **isort**: Import sorting
3. **flake8**: Linting
4. **mypy**: Type checking
5. **radon**: Complexity analysis

### Flake8 Configuration

See `.flake8` for project configuration:

```ini
[flake8]
max-line-length = 88
max-complexity = 10
ignore = W503, E203
per-file-ignores =
    app/frontend/*.py:F403,F405
```

### Commands

```bash
# Format code
black .

# Sort imports
isort .

# Lint
flake8 app/ scripts/

# Type check
mypy app/

# Check complexity
radon cc app/ -n C  # Show C+ complexity
```

### Pre-Push Validation

**Required before pushing**:

```bash
# Environment validation
python scripts/validate_environment.py

# Static analysis
python scripts/static_analysis_audit.py

# Integration tests
pytest test_phase4_integration.py -v
```

---

## Checklist for New Code

Before committing, verify:

- [ ] Black formatting applied
- [ ] Imports sorted with isort
- [ ] No flake8 errors (except documented suppressions)
- [ ] Type hints on all functions
- [ ] Docstrings on public APIs
- [ ] Complexity ≤ 10 (B-level or better)
- [ ] Specific exception handling (no bare except)
- [ ] Tests added/updated
- [ ] Static analysis passes (100%)
- [ ] Integration tests pass (8/8)

---

## Evolution and Updates

**This guide is living documentation.**

### Update Process

1. Propose changes via pull request
2. Document rationale in PR description
3. Update this guide + relevant docs
4. Get team approval

### Version History

| Version | Date | Changes | Phase |
|---------|------|---------|-------|
| 1.0 | 2025-10-06 | Initial version consolidating Phase 4.2.6 decisions | Phase 4.2.6 Phase 2B |

---

## References

1. **PEP 8**: https://peps.python.org/pep-0008/
2. **Black**: https://black.readthedocs.io/
3. **Flake8**: https://flake8.pycqa.org/
4. **Pydantic V2**: https://docs.pydantic.dev/latest/
5. **FastHTML Docs**: https://docs.fasthtml.dev/
6. **Our Validation Standards**: `docs/VALIDATION_STANDARDS.md`
7. **FastHTML Justification**: `docs/FASTHTML_PATTERN_JUSTIFICATION.md`
8. **Complexity Documentation**: `docs/COMPLEXITY_C_FUNCTIONS_DOCUMENTATION.md`

---

**Document Status**: ✅ OFFICIAL  
**Enforcement**: MANDATORY for all new code  
**Next Review**: Quarterly or after major refactorings
