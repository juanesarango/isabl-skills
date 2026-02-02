#!/bin/bash
# Deploy AGENTS.md templates to Isabl repositories
# Creates AGENTS.md and symlinks for tool-specific files

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATES_DIR="$SCRIPT_DIR/../templates"
ISABL_DIR="$HOME/isabl"

deploy_to_repo() {
    local repo_name="$1"
    local template_file="$2"
    local repo_path="$ISABL_DIR/$repo_name"

    if [ ! -d "$repo_path" ]; then
        echo "Skipping $repo_name: directory not found"
        return
    fi

    if [ ! -f "$TEMPLATES_DIR/$template_file" ]; then
        echo "Skipping $repo_name: template $template_file not found"
        return
    fi

    echo "Deploying to $repo_name..."

    # Copy AGENTS.md
    cp "$TEMPLATES_DIR/$template_file" "$repo_path/AGENTS.md"

    # Create symlinks for tool-specific files
    cd "$repo_path"

    # Claude Code
    ln -sf AGENTS.md CLAUDE.md

    # Cursor
    ln -sf AGENTS.md .cursorrules

    # Windsurf
    ln -sf AGENTS.md .windsurfrules

    # GitHub Copilot
    mkdir -p .github
    ln -sf ../AGENTS.md .github/copilot-instructions.md

    echo "  Created: AGENTS.md, CLAUDE.md, .cursorrules, .windsurfrules, .github/copilot-instructions.md"
}

echo "Deploying AGENTS.md templates..."
echo ""

deploy_to_repo "isabl_cli" "isabl_cli.md"
deploy_to_repo "isabl_web" "isabl_web.md"
deploy_to_repo "register_apps" "register_apps.md"

echo ""
echo "Done! Review changes in each repo before committing."
