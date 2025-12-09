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

## Ollama Setup for E2E Tests

### What is Ollama?

Ollama is a **local LLM runtime** that allows running AI models on your machine. It serves as:
- **Budget fallback**: Free alternative when API credits exhausted
- **Privacy mode**: Data stays on your device
- **Offline operation**: Works without internet

### Installation

#### macOS
```bash
brew install ollama
```

#### Linux
```bash
curl https://ollama.ai/install.sh | sh
```

#### Windows
Download installer from: https://ollama.ai/download

### Starting Ollama Service

```bash
# Start Ollama server (run in separate terminal)
ollama serve

# Server will run on http://localhost:11434
```

### Installing Required Models

#### Essential Model (Required for E2E Tests)
```bash
# Primary model used in tests (4GB RAM required)
ollama pull llama2:7b
```

#### Optional Models (Extended Testing)
```bash
# Better French support (4GB RAM)
ollama pull mistral:7b

# Optimized for conversations (4GB RAM)
ollama pull neural-chat:7b

# Technical/coding use cases (4GB RAM)
ollama pull codellama:7b

# Higher quality, larger model (8GB RAM)
ollama pull llama2:13b
```

### Verifying Installation

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Should return JSON with installed models
# Example:
# {
#   "models": [
#     {"name": "llama2:7b", "size": 3826793677, ...}
#   ]
# }

# List installed models
ollama list

# Example output:
# NAME            ID              SIZE      MODIFIED
# llama2:7b       78e26419b446    3.8 GB    2 days ago
# mistral:7b      6577803aa9a0    4.1 GB    1 week ago
```

### Running Ollama E2E Tests

```bash
# Run only Ollama E2E tests
pytest tests/e2e/test_ai_e2e.py::TestOllamaE2E -v -s

# Run specific Ollama test
pytest tests/e2e/test_ai_e2e.py::TestOllamaE2E::test_ollama_real_conversation_english -v -s

# Run all E2E tests including Ollama
pytest tests/e2e/ -v -m e2e
```

### Test Coverage

The `TestOllamaE2E` class includes 7 comprehensive tests:

1. **test_ollama_service_availability** - Validates service is running
2. **test_ollama_real_conversation_english** - Real English conversation
3. **test_ollama_multi_language_support** - Tests English, French, Spanish
4. **test_ollama_model_selection** - Validates model selection logic
5. **test_ollama_budget_exceeded_fallback** - Tests fallback when budget exceeded
6. **test_ollama_response_quality** - Validates response quality standards
7. **test_ollama_privacy_mode** - Verifies local processing and privacy

### What Ollama E2E Tests Validate

✅ **Service Availability**
- Ollama server is running and accessible
- Models are installed and ready
- Health status reporting works

✅ **Real Conversations**
- Generates actual responses (not mocked)
- Handles multiple languages correctly
- Selects appropriate models for each language

✅ **Budget Fallback**
- System falls back to Ollama when budget exceeded
- Fallback mechanism works end-to-end
- Users get responses without API costs

✅ **Response Quality**
- Responses are coherent and appropriate
- Response times are reasonable (< 30s)
- No error messages in responses

✅ **Privacy Mode**
- All processing happens locally
- No external API calls made
- Data never leaves the device

### Troubleshooting

#### Error: "Ollama service not running"

**Solution:**
```bash
# Start Ollama server
ollama serve

# Verify it's running
curl http://localhost:11434/api/tags
```

If still failing:
- Check if port 11434 is already in use
- Try restarting: `killall ollama && ollama serve`
- Check Ollama logs for errors

#### Error: "llama2:7b model not installed"

**Solution:**
```bash
# Pull the required model
ollama pull llama2:7b

# Verify installation
ollama list

# Should show llama2:7b in the list
```

#### Error: "Connection refused" or "Cannot connect to server"

**Causes:**
- Ollama server not running
- Firewall blocking port 11434
- Ollama installed but not started

**Solution:**
1. Start Ollama: `ollama serve`
2. Check firewall settings
3. Verify installation: `which ollama`

#### Slow Response Times (> 30 seconds)

**Normal behavior:**
- **First request**: 10-30 seconds (model loading into RAM)
- **Subsequent requests**: 3-15 seconds (model already loaded)

**If consistently slow:**
- Close other memory-intensive applications
- Consider using smaller model (llama2:7b vs llama2:13b)
- Check available RAM (7b models need ~4GB free)

#### Model Loading Failures

**Error:** `failed to load model`

**Causes:**
- Insufficient RAM
- Corrupted model file
- Disk space issues

**Solution:**
```bash
# Remove and re-pull model
ollama rm llama2:7b
ollama pull llama2:7b

# Check disk space
df -h

# Check available RAM
free -h  # Linux
vm_stat  # macOS
```

### Performance Expectations

#### Response Times (llama2:7b on M1 Mac)
- **First request**: 15-25 seconds (model loading)
- **Warm requests**: 5-12 seconds (model in RAM)
- **Streaming**: Starts in 3-5 seconds

#### Memory Usage
- **llama2:7b**: ~4GB RAM
- **llama2:13b**: ~8GB RAM
- **mistral:7b**: ~4GB RAM
- **neural-chat:7b**: ~4GB RAM

#### Disk Space
- **llama2:7b**: ~3.8GB
- **llama2:13b**: ~7.3GB
- **mistral:7b**: ~4.1GB

### Advanced Configuration

#### Custom Ollama Host

If running Ollama on different host/port:

```bash
# Set in .env file
OLLAMA_HOST=http://custom-host:11434

# Or export environment variable
export OLLAMA_HOST=http://192.168.1.100:11434
```

#### GPU Acceleration

Ollama automatically uses GPU if available:
- **NVIDIA GPUs**: CUDA (Linux/Windows)
- **Apple Silicon**: Metal (macOS M1/M2/M3)
- **AMD GPUs**: ROCm (Linux)

Check GPU usage:
```bash
# NVIDIA
nvidia-smi

# Apple Silicon (Activity Monitor → GPU)
```

### Cost Comparison

| Provider | Cost per 1M tokens | Notes |
|----------|-------------------|-------|
| Claude | $3.00 - $15.00 | High quality, API costs |
| Mistral | $0.25 - $2.00 | Cost-effective, API costs |
| DeepSeek | $0.14 - $0.28 | Very cheap, API costs |
| **Ollama** | **$0.00** | **Free, local processing** |

**Ollama Advantages:**
- ✅ Zero cost (no API fees)
- ✅ Complete privacy (data stays local)
- ✅ Offline capability
- ✅ No rate limits

**Ollama Trade-offs:**
- ⚠️ Requires local resources (RAM, disk)
- ⚠️ Slower than cloud APIs
- ⚠️ Lower quality than Claude/GPT-4
- ⚠️ Limited to available models

### When Ollama E2E Tests Run

**Auto-skip conditions:**
- ❌ Ollama not installed → Test skips gracefully
- ❌ Ollama not running → Test skips with instructions
- ❌ llama2:7b not installed → Test skips with command

**Tests execute when:**
- ✅ Ollama service running (`ollama serve`)
- ✅ llama2:7b model installed
- ✅ Service reachable at localhost:11434

### Best Practices

1. **Keep Ollama running** during development for instant fallback
2. **Install multiple models** for language diversity
3. **Monitor RAM usage** with large models
4. **Update regularly**: `ollama pull <model>` to get latest versions
5. **Test fallback scenarios** to ensure budget limits work correctly

### Resources

- **Ollama Website**: https://ollama.ai/
- **Ollama GitHub**: https://github.com/ollama/ollama
- **Model Library**: https://ollama.ai/library
- **Documentation**: https://github.com/ollama/ollama/tree/main/docs

---

## Questions?

If unsure whether to run E2E tests, ask yourself:
1. Do I need to verify real API functionality?
2. Am I okay with spending API credits?
3. Have I checked that my API keys are secure?

If YES to all three → Safe to run E2E tests
If NO to any → Use unit or integration tests instead

---

**Remember**: E2E tests are powerful but expensive. Use them wisely! 💰

**Ollama Exception**: Ollama E2E tests are FREE and can be run frequently! 🎉
