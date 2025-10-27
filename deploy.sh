#!/bin/bash

echo "========================================="
echo "ML Competition Platform - Cloud Deploy"
echo "========================================="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "Initializing git repository..."
    git init
    echo ""
fi

# Generate secret key
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
echo "Generated SECRET_KEY: $SECRET_KEY"
echo "Save this for your deployment platform!"
echo ""

# Add all files
echo "Adding files to git..."
git add .
git status
echo ""

# Commit
echo "Creating commit..."
git commit -m "Prepare for cloud deployment" || echo "No changes to commit"
echo ""

echo "========================================="
echo "Next Steps:"
echo "========================================="
echo ""
echo "Choose a deployment platform:"
echo ""
echo "1. RAILWAY (Recommended - Easiest)"
echo "   - Go to: https://railway.app"
echo "   - Sign up with GitHub"
echo "   - Push this repo to GitHub first:"
echo "     git remote add origin YOUR_GITHUB_URL"
echo "     git push -u origin main"
echo "   - Deploy from GitHub in Railway"
echo "   - Set environment variable:"
echo "     SECRET_KEY=$SECRET_KEY"
echo ""
echo "2. RENDER"
echo "   - Go to: https://render.com"
echo "   - Connect GitHub repo"
echo "   - Deploy as Web Service"
echo "   - Set environment variable:"
echo "     SECRET_KEY=$SECRET_KEY"
echo ""
echo "3. Use Railway CLI (fastest):"
echo "   curl -fsSL https://railway.app/install.sh | sh"
echo "   railway login"
echo "   railway init"
echo "   railway up"
echo "   railway variables set SECRET_KEY=$SECRET_KEY"
echo "   railway variables set ENVIRONMENT=production"
echo ""
echo "See DEPLOYMENT.md for detailed instructions!"
echo "========================================="
