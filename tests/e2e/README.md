# End-to-End (E2E) Tests

## ⚠️ CRITICAL SECURITY WARNINGS ⚠️

### 🔴 DO NOT COMMIT API KEYS TO GITHUB! 🔴

E2E tests use **REAL API keys** from your `.env` file and make **REAL API calls** to external services. This means:

1. **NEVER commit `.env` file** - It must remain in `.gitignore`
2. **NEVER hardcode API keys** in test files
3. **NEVER run E2E tests in CI/CD** unless you have a secure secrets management system
4. **E2E tests cost real money** - They consume API credits

## What are E2E Tests?

E2E (End-to-End) tests verify that the entire system works correctly with real external services:

- **Real AI APIs**: Claude, Mistral, Qwen
- **Real TTS/STT**: Piper TTS, speech recognition
- **Real database**: Actual database connections
- **Real costs**: Each test run consumes API credits

## Test Tiers

This project uses a **3-tier testing strategy**:

### Tier 1: Unit Tests (Fast, Isolated)
- **Location**: `tests/test_*.py`
- **Speed**: < 1 second per test
- **Mocking**: All external services mocked
- **Purpose**: Test code logic in isolation
- **Run**: `pytest tests/ -m "not integration and not e2e"`

### Tier 2: Integration Tests (Component Interaction)
- **Location**: `tests/integration/`
- **Speed**: 1-5 seconds per test
- **Mocking**: External APIs mocked, internal services real
- **Purpose**: Verify component interaction and failover
- **Run**: `pytest tests/integration/ -m integration`

### Tier 3: E2E Tests (Real Services) - **MANUAL ONLY**
- **Location**: `tests/e2e/`
- **Speed**: 5-30 seconds per test
- **Mocking**: No mocking - everything is real
- **Purpose**: Verify actual functionality with real services
- **Run**: `pytest tests/e2e/ -m e2e` (MANUAL EXECUTION ONLY)

## When to Run E2E Tests

E2E tests should be run:
- ✅ **Manually** before major releases
- ✅ **Manually** when debugging production issues
- ✅ **Manually** when verifying API integrations
- ❌ **NEVER** in automated CI/CD (unless secure secrets management)
- ❌ **NEVER** on every commit (too expensive)

## How to Run E2E Tests

### Prerequisites

1. **Valid `.env` file** with real API keys:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-...
   MISTRAL_API_KEY=...
   # etc.
   ```

2. **Sufficient API credits** in your accounts

3. **Understanding of costs** - Each test consumes credits

### Running E2E Tests

```bash
# Activate virtual environment
source ai-tutor-env/bin/activate

# Run ALL E2E tests (COSTS MONEY!)
pytest tests/e2e/ -v -m e2e

# Run specific E2E test
pytest tests/e2e/test_ai_e2e.py::test_claude_real_api -v -m e2e

# Run E2E tests with detailed output
pytest tests/e2e/ -v -s -m e2e
```

### Safety Checks

Before running E2E tests, verify:

```bash
# Check .env file exists
ls -la .env

# Verify .env is in .gitignore
grep "\.env" .gitignore

# Check git status (ensure .env not staged)
git status
```

## E2E Test Structure

E2E tests are structured to:

1. **Skip if no API keys** - Tests auto-skip if `.env` keys missing
2. **Log costs** - Each test logs estimated API cost
3. **Cleanup resources** - Tests clean up after themselves
4. **Fail fast** - Stop on first critical failure

## Example E2E Test

```python
import pytest
import os
from dotenv import load_dotenv

# Mark as E2E test
pytestmark = pytest.mark.e2e

class TestClaudeE2E:
    """E2E tests for Claude AI service"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Load .env and check for API key"""
        load_dotenv()
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not found in .env")
    
    @pytest.mark.asyncio
    async def test_claude_real_api_call(self):
        """Test actual Claude API call"""
        from app.services.claude_service import ClaudeService
        
        service = ClaudeService()
        response = await service.generate_response(
            messages=[{"role": "user", "content": "Say hello"}],
            message="Say hello",
            language="en"
        )
        
        assert response is not None
        assert response.content is not None
        assert len(response.content) > 0
        print(f"✅ Test passed. Estimated cost: ${response.cost:.4f}")
```

## Security Best Practices

### ✅ DO:
- Store API keys in `.env` file
- Add `.env` to `.gitignore`
- Run E2E tests manually
- Document costs and limitations
- Use test API keys (if providers offer them)
- Monitor API usage after E2E runs

### ❌ DON'T:
- Commit `.env` to Git
- Hardcode API keys in code
- Run E2E tests in CI/CD without secure secrets
- Run E2E tests on every commit
- Share API keys in test files
- Ignore API costs

## Troubleshooting

### Error: "API key not found"
```bash
# Solution: Create/check .env file
cp .env.example .env  # If exists
# Then add your real API keys
```

### Error: "Rate limit exceeded"
```bash
# Solution: Wait or upgrade API plan
# AI services have rate limits
```

### Error: "Insufficient credits"
```bash
# Solution: Add credits to API account
# Each test consumes credits
```

## Cost Estimation

Typical E2E test costs (approximate):
- Claude API call: $0.001 - $0.01 per test
- Mistral API call: $0.0005 - $0.005 per test
- Qwen API call: $0.0005 - $0.005 per test
- Full E2E suite: $0.10 - $1.00 per run

**Monitor your API usage regularly!**

## Questions?

If unsure whether to run E2E tests, ask yourself:
1. Do I need to verify real API functionality?
2. Am I okay with spending API credits?
3. Have I checked that my API keys are secure?

If YES to all three → Safe to run E2E tests
If NO to any → Use unit or integration tests instead

---

**Remember**: E2E tests are powerful but expensive. Use them wisely! 💰
