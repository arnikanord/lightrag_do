#!/bin/bash
# Quick script to setup GitHub repository

set -e

echo "=== GAFTA Guardian - GitHub Setup ==="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "Initializing git repository..."
    git init
fi

# Check if remote exists
if ! git remote | grep -q origin; then
    echo ""
    echo "Please provide your GitHub repository URL:"
    echo "Example: https://github.com/username/gafta-guardian.git"
    read -p "Repository URL: " REPO_URL
    
    if [ -n "$REPO_URL" ]; then
        git remote add origin "$REPO_URL"
        echo "✓ Remote added: $REPO_URL"
    else
        echo "⚠ No URL provided. Add remote manually:"
        echo "  git remote add origin https://github.com/username/gafta-guardian.git"
    fi
else
    echo "✓ Git remote already configured"
    git remote -v
fi

echo ""
echo "=== Files to be committed ==="
git status --short | head -20

echo ""
echo "=== Ready to commit ==="
echo ""
echo "Run these commands to push to GitHub:"
echo ""
echo "  git add ."
echo "  git commit -m 'Save GAFTA Guardian implementation'"
echo "  git branch -M main"
echo "  git push -u origin main"
echo ""
echo "Or run this script with --commit flag to auto-commit:"
echo "  bash setup_github.sh --commit"
echo ""

if [ "$1" == "--commit" ]; then
    echo "Auto-committing..."
    git add .
    git commit -m "Save GAFTA Guardian implementation - $(date +%Y-%m-%d)" || echo "Nothing to commit"
    echo "✓ Committed"
    echo ""
    echo "Now push with:"
    echo "  git push -u origin main"
fi
