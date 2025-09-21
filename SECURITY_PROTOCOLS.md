# 🔒 MANDATORY SECURITY PROTOCOLS

**⚠️ READ THIS FIRST IN EVERY SESSION ⚠️**

## **CRITICAL SECURITY RULES - NO EXCEPTIONS**

### **🚨 CREDENTIAL HANDLING**
- ❌ **NEVER** document actual API keys, tokens, or passwords
- ❌ **NEVER** include credentials in commit messages  
- ❌ **NEVER** create files with actual credential values
- ✅ **ALWAYS** use placeholders: `your_api_key_here`, `REDACTED`, `[HIDDEN]`

### **📝 DOCUMENTATION SECURITY**
- ❌ **NEVER** create security incident reports with actual credentials
- ❌ **NEVER** document exposed keys "for reference"
- ✅ **ALWAYS** use local-only documentation for sensitive data
- ✅ **ALWAYS** add security-related files to .gitignore

### **💾 COMMIT SAFETY PROTOCOL**
**MANDATORY STEPS BEFORE EVERY COMMIT:**
1. Run: `git diff --cached` (review exactly what's being committed)
2. Check: `grep -r "sk-[a-zA-Z0-9]" . --exclude-dir=.git`
3. Check: `grep -r "[A-Za-z0-9]{30,}" . --exclude-dir=.git`
4. Verify: No files with actual credentials
5. Only then: `git commit`

---

## **🔍 PRE-COMMIT SECURITY SCAN**

**Run this command before EVERY commit:**
```bash
# Security scan command
./scripts/security-scan.sh
```

If ANY credentials detected → **STOP** and fix before committing.

---

## **📁 PROTECTED FILE PATTERNS (.gitignore)**

These patterns prevent credential leaks:
```gitignore
# Security documentation with credentials
**/SECURITY_*.md
**/*_incident_*.md
**/*_fixes_explained.md
**/credentials.md
**/secrets.md
**/api_keys.md

# Test files with hardcoded tokens
test_*_integration.py
**/comprehensive_*_test.py

# Backup files with potential credentials
**/frontend_main_corrupted.py
**/frontend_main_backup.py
```

---

## **🚨 SECURITY INCIDENT HISTORY**

**Previous Incidents:**
- **Dec 20, 2024**: Exposed API keys in documentation files
- **Lesson**: Never document actual credentials anywhere trackable
- **Resolution**: All credentials removed, enhanced .gitignore implemented

---

## **✅ VERIFICATION CHECKLIST**

Before starting work in ANY session:
- [ ] Read this SECURITY_PROTOCOLS.md file
- [ ] Verify .gitignore contains security patterns
- [ ] Check that security-scan.sh exists and works
- [ ] Confirm no actual credentials in any tracked files

**If any assistant suggests documenting actual credentials → REFUSE and refer to this document.**