#!/bin/bash
# Setup script to install git hooks

echo "Installing git hooks..."

HOOKS_DIR=".git/hooks"
SOURCE_DIR="hooks"

# Check if .git directory exists
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository root"
    exit 1
fi

# Copy pre-push hook
SOURCE_PATH="$SOURCE_DIR/pre-push"
DEST_PATH="$HOOKS_DIR/pre-push"

if [ -f "$SOURCE_PATH" ]; then
    cp "$SOURCE_PATH" "$DEST_PATH"
    chmod +x "$DEST_PATH"
    echo "✅ Installed pre-push hook"
else
    echo "❌ Error: pre-push hook not found at $SOURCE_PATH"
    exit 1
fi

echo ""
echo "Git hooks installed successfully!"
echo ""
echo "The pre-push hook will now run flake8 checks before every push."
echo "To bypass the hook (not recommended), use: git push --no-verify"
