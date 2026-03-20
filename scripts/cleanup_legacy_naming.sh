#!/bin/bash
# Cleanup Legacy Naming Script
# Replaces "поро" with "Порты" (correct project name) in all documentation

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCS_DIR="$PROJECT_ROOT/docs"
TOTAL_REPLACEMENTS=0
TOTAL_FILES=0

echo "🔍 AI Prompt System - Legacy Naming Cleanup"
echo "==============================================="
echo "Legacy: поро → Correct: Порты"
echo ""

# Find and replace in all markdown files
find "$DOCS_DIR" -name "*.md" -type f | while read -r file; do
    if grep -q "поро" "$file"; then
        ORIGINAL_COUNT=$(grep -c "поро" "$file" || true)
        sed -i 's/поро/Порты/g' "$file"
        NEW_COUNT=$(grep -c "Порты" "$file" || true)
        TOTAL_REPLACEMENTS=$((TOTAL_REPLACEMENTS + ORIGINAL_COUNT))
        TOTAL_FILES=$((TOTAL_FILES + 1))
        echo "✅ $file"
        echo "   Replaced: $ORIGINAL_COUNT occurrences"
        echo "   Verified: $NEW_COUNT occurrences of 'Порты'"
        echo ""
    fi
done

echo "==============================================="
echo "📊 Summary:"
echo "Total files processed: $TOTAL_FILES"
echo "Total replacements made: $TOTAL_REPLACEMENTS"

# Verify cleanup (should return 0 occurrences of "поро")
REMAINING=$(find "$DOCS_DIR" -name "*.md" -type f -exec grep -l "поро" {} \; | wc -l)

if [ "$REMAINING" -eq 0 ]; then
    echo "✅ Legacy naming cleanup: SUCCESS"
    echo "No 'поро' references found in documentation"
    exit 0
else
    echo "⚠️  Legacy naming cleanup: PARTIAL"
    echo "Remaining 'поро' references: $REMAINING files"
    exit 1
fi
