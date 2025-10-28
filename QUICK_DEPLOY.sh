#!/bin/bash
# Quick Deployment Script
# Run this to prepare for GitHub push

echo "🚀 ML Competition Platform - Serverless Deployment"
echo "=================================================="
echo ""

# Check git status
echo "📋 Step 1: Checking git status..."
git status
echo ""

# Ask for confirmation
read -p "Ready to commit and push? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "❌ Cancelled"
    exit 1
fi

# Add all files
echo "📦 Step 2: Adding all files..."
git add .
echo "✅ Files added"
echo ""

# Commit
echo "💾 Step 3: Committing changes..."
git commit -m "Serverless version with inline RMSE calculation"
echo "✅ Changes committed"
echo ""

# Check if remote exists
if git remote | grep -q origin; then
    echo "🌐 Step 4: Pushing to GitHub..."
    git push origin main || git push origin master
    echo "✅ Pushed to GitHub"
else
    echo "⚠️  No remote repository configured"
    echo ""
    echo "Please add your GitHub repository:"
    echo "git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
    echo "git push -u origin main"
fi

echo ""
echo "=================================================="
echo "✅ READY FOR DEPLOYMENT!"
echo "=================================================="
echo ""
echo "📖 Next Steps:"
echo "1. Go to https://supabase.com - Setup database"
echo "2. Go to https://vercel.com - Deploy project"
echo "3. Read DEPLOY_NOW.md for detailed steps"
echo ""
echo "Good luck! 🚀"
