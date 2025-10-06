#!/bin/bash
# Quick fix script to remove mock data fallbacks from frontend components
# Run this from marketingiq-platform directory

set -e

echo "========================================="
echo "Applying Quick Fixes to MarketingIQ Platform"
echo "========================================="
echo ""

# Backup original files
echo "[1/3] Creating backups..."
mkdir -p .backups/$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=".backups/$(date +%Y%m%d_%H%M%S)"

# Components with mock fallbacks
MOCK_COMPONENTS=(
    "web/src/agents/optimization_agent/KeywordOptimizer.tsx"
    "web/src/agents/optimization_agent/CampaignSimulator.tsx"
    "web/src/agents/insight_agent/InsightsSummary.tsx"
    "web/src/agents/insight_agent/AnomalyDetection.tsx"
    "web/src/agents/forecasting_agent/ScenarioSimulator.tsx"
    "web/src/agents/forecasting_agent/CTRForecast.tsx"
    "web/src/agents/data_agent/CampaignsDashboard.tsx"
    "web/src/agents/alert_agent/ThresholdsMonitor.tsx"
)

for file in "${MOCK_COMPONENTS[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/$(basename $file)"
        echo "  Backed up: $file"
    fi
done

echo ""
echo "[2/3] Removing mock data fallbacks..."

# This is a placeholder - actual implementation would require
# more sophisticated parsing or manual edits
echo "  WARNING: This requires manual code changes."
echo "  Please refer to DASHBOARD_VERIFICATION_SUMMARY.md for specific edits."

echo ""
echo "[3/3] Adding formatter imports..."

# Add import statement to components that use inline currency formatting
CURRENCY_COMPONENTS=(
    "web/src/agents/forecasting_agent/SpendForecast.tsx"
    "web/src/agents/optimization_agent/BudgetOptimizer.tsx"
    "web/src/agents/data_agent/KeywordsDashboard.tsx"
    "web/src/agents/data_agent/SearchTermsDashboard.tsx"
)

for file in "${CURRENCY_COMPONENTS[@]}"; do
    if [ -f "$file" ]; then
        # Check if import already exists
        if ! grep -q "from '@/utils/formatters'" "$file"; then
            # Add import after other imports (simplified - may need adjustment)
            echo "  Adding formatter import to: $file"
            # Note: This is a placeholder - actual implementation would use sed/awk
        fi
    fi
done

echo ""
echo "========================================="
echo "Quick fixes preparation complete!"
echo "========================================="
echo ""
echo "IMPORTANT: This script created backups only."
echo "Manual code changes are required. See:"
echo "  - reports/DASHBOARD_VERIFICATION_SUMMARY.md"
echo "  - scripts/patches/ directory"
echo ""
echo "Backups saved to: $BACKUP_DIR"
echo ""
