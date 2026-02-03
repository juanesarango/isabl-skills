#!/bin/bash
# Install Isabl skills to ~/.claude/skills/
# Usage: ./scripts/install-skills.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SRC="$SCRIPT_DIR/../skills"
SKILLS_DST="$HOME/.claude/skills/isabl"

echo "Isabl Skills Installer"
echo "======================"
echo ""

# Check if source skills exist
if [ ! -d "$SKILLS_SRC" ]; then
    echo -e "${RED}Error: Skills directory not found at $SKILLS_SRC${NC}"
    exit 1
fi

# Create destination directory
mkdir -p "$SKILLS_DST"

# Count skills
SKILL_COUNT=$(ls -1 "$SKILLS_SRC"/*.md 2>/dev/null | wc -l | tr -d ' ')

if [ "$SKILL_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}Warning: No skills found in $SKILLS_SRC${NC}"
    exit 0
fi

echo "Installing $SKILL_COUNT skills to $SKILLS_DST..."
echo ""

# Copy each skill
for skill in "$SKILLS_SRC"/*.md; do
    if [ -f "$skill" ]; then
        skill_name=$(basename "$skill")
        cp "$skill" "$SKILLS_DST/$skill_name"
        echo -e "${GREEN}✓${NC} Installed: $skill_name"
    fi
done

echo ""
echo -e "${GREEN}Done!${NC} Skills installed to $SKILLS_DST"
echo ""
echo "Usage in Claude Code:"
echo "  /isabl-write-app     - Create a new Isabl application"
echo "  /isabl-debug-analysis - Debug a failed analysis"
echo "  /isabl-query-data    - Query data from Isabl"
echo ""
echo "To update skills, run this script again."
