#!/bin/bash
# 🔒 Setup Git Security Hooks
# Run this once to install automatic security checks

echo "🔧 Setting up Git security hooks..."

# Create .git/hooks directory if it doesn't exist
mkdir -p .git/hooks

# Create pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# 🔒 Pre-commit security hook
# Automatically runs security scan before every commit

echo "🔍 Running automatic security scan..."

# Run the security scanner
./scripts/security-scan.sh

# Exit with scanner's exit code
exit $?
EOF

# Make pre-commit hook executable
chmod +x .git/hooks/pre-commit

# Create commit-msg hook to check commit messages
cat > .git/hooks/commit-msg << 'EOF'
#!/bin/bash
# 🔒 Commit message security hook
# Prevents committing credentials in commit messages

commit_msg_file=$1
commit_msg=$(cat "$commit_msg_file")

# Check for potential credentials in commit message
if echo "$commit_msg" | grep -qE "(sk-[a-zA-Z0-9]|eyJ[A-Za-z0-9]|[A-Za-z0-9]{30,})"; then
    echo "🚨 ERROR: Potential credential detected in commit message!"
    echo "❌ Commit blocked for security"
    exit 1
fi

echo "✅ Commit message security check passed"
exit 0
EOF

# Make commit-msg hook executable
chmod +x .git/hooks/commit-msg

echo "✅ Git security hooks installed successfully!"
echo ""
echo "🛡️  Security features now active:"
echo "   • Pre-commit credential scanning"
echo "   • Commit message security validation"
echo "   • Automatic blocking of unsafe commits"
echo ""
echo "🚀 To test: Run 'git commit' - security scan will run automatically"
