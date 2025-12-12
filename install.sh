#!/bin/bash

set -e

echo "🚀 Installing Project Management..."
echo ""

# Check if skill.md exists to determine if this is local or remote install
if [ -f "skills/project-management.md" ]; then
    LOCAL_INSTALL=true
else
    LOCAL_INSTALL=false
fi

if [ "$LOCAL_INSTALL" = true ]; then
    # Local installation
    MARKETPLACE_PATH=$(pwd)
    echo "🔧 Adding local marketplace from: $MARKETPLACE_PATH"
    claude plugin marketplace add "$MARKETPLACE_PATH"

    echo "📦 Installing project-management from local marketplace..."
    claude plugin install project-management@project-management-marketplace
else
    # Remote installation (clone from GitHub)
    echo "📥 Cloning project-management from GitHub..."
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"

    git clone https://github.com/syfyufei/project-management.git
    cd project-management

    MARKETPLACE_PATH=$(pwd)
    echo "🔧 Adding marketplace from: $MARKETPLACE_PATH"
    claude plugin marketplace add "$MARKETPLACE_PATH"

    echo "📦 Installing project-management..."
    claude plugin install project-management@project-management-marketplace

    # Cleanup
    cd ~
    rm -rf "$TEMP_DIR"
fi

echo ""
echo "✅ Project Management installed successfully!"
echo ""
echo "Verify installation:"
echo "  /help"
echo ""
echo "Get started with natural language or slash commands"
echo ""
