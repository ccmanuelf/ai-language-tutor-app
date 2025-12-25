# Environment Setup Guide

## ⚠️ CRITICAL: Always Use Virtual Environment

**NEVER use global Python for this project.** Always activate the virtual environment first.

## Virtual Environment Location

```
ai-tutor-env/
```

## Activation Commands

### MacOS/Linux
```bash
source ai-tutor-env/bin/activate
```

### Windows
```bash
ai-tutor-env\Scripts\activate
```

### Direct Usage (Without Activation)
```bash
# Run Python
./ai-tutor-env/bin/python

# Run pip
./ai-tutor-env/bin/pip

# Run pytest
./ai-tutor-env/bin/pytest
```

## Quick Health Check

After activation, verify your environment:

```bash
# Should show: True
python -c "import sys; print('In venv:', hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))"

# Should show: No broken requirements found
pip check

# Should show all services available
python -c "
from app.services.claude_service import claude_service
from app.services.mistral_service import mistral_service
print('Claude:', claude_service.is_available)
print('Mistral:', mistral_service.is_available)
"
```

## Installing/Updating Dependencies

**ALWAYS** use the virtual environment:

```bash
# Activate first
source ai-tutor-env/bin/activate

# Install from requirements
pip install -r requirements.txt

# Or direct usage
./ai-tutor-env/bin/pip install -r requirements.txt
```

## Current Dependencies Status

✅ **Production-Grade Setup**
- No dependency conflicts
- All required libraries installed:
  - `anthropic==0.64.0` (Claude API)
  - `mistralai==1.9.9` (Mistral API)
  - `openai==1.3.7` (DeepSeek/Qwen via OpenAI client)
  - `httpx==0.28.1` (HTTP client)
  - All other dependencies in requirements.txt

## Common Issues & Solutions

### Issue: "Claude/Mistral API not available"
**Cause**: Running with global Python instead of virtual environment  
**Solution**: Activate virtual environment first

### Issue: Dependency conflicts with aider-chat/litellm
**Cause**: Using global Python which has dev tools installed  
**Solution**: Use virtual environment - it's isolated and clean

### Issue: Tests fail with import errors
**Cause**: Not using virtual environment  
**Solution**: `source ai-tutor-env/bin/activate` or use `./ai-tutor-env/bin/pytest`

## Verification Commands

```bash
# Check Python location (should be in ai-tutor-env/)
which python

# Check pip location (should be in ai-tutor-env/)
which pip

# Check for dependency issues (should show: No broken requirements)
pip check

# Run all tests (should pass)
pytest tests/ -q
```

## IDE Setup

### VSCode
Add to `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/ai-tutor-env/bin/python"
}
```

### PyCharm
1. Settings → Project → Python Interpreter
2. Select existing interpreter
3. Choose: `<project>/ai-tutor-env/bin/python`

## Emergency: Recreate Virtual Environment

If virtual environment is corrupted:

```bash
# Remove old environment
rm -rf ai-tutor-env

# Create new one
python3 -m venv ai-tutor-env

# Activate
source ai-tutor-env/bin/activate

# Install all dependencies
pip install -r requirements.txt

# Verify
pip check
pytest tests/ -q
```

## Environment Variables

Required in `.env` file:
- `ANTHROPIC_API_KEY` - Claude API key
- `MISTRAL_API_KEY` - Mistral API key
- `DEEPSEEK_API_KEY` - DeepSeek API key
- (Optional) `QWEN_API_KEY` - Qwen API key

Check `.env.example` for full list.

---

**Last Updated**: 2025-11-06  
**Status**: ✅ Production-Grade Environment
