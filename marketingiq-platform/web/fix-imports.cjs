/**
 * Script to fix import paths in all migrated dashboards
 * Run: node fix-imports.js
 */
const fs = require('fs');
const path = require('path');

const agentsDir = './src/components/dashboards/agents';

// Import path mappings (old → new)
const importMappings = [
  // Common components
  { from: "from '../../components/common/", to: "from '../../../common/" },
  { from: 'from "../../components/common/', to: 'from "../../../common/' },

  // KPI components
  { from: "from '../../components/kpi/", to: "from '../../../kpi/" },
  { from: 'from "../../components/kpi/', to: 'from "../../../kpi/' },

  // Chart components
  { from: "from '../../components/charts/", to: "from '../../../charts/" },
  { from: 'from "../../components/charts/', to: 'from "../../../charts/' },

  // Context
  { from: "from '../../context/FilterContext'", to: "from '../../../../context/FilterContext'" },
  { from: 'from "../../context/FilterContext"', to: 'from "../../../../context/FilterContext"' },

  // Hooks
  { from: "from '../../hooks/", to: "from '../../../../hooks/" },
  { from: 'from "../../hooks/', to: 'from "../../../../hooks/' },

  // Config
  { from: "from '../../config/", to: "from '../../../../config/" },
  { from: 'from "../../config/', to: 'from "../../../../config/' },

  // Services
  { from: "from '../../services/", to: "from '../../../../services/" },
  { from: 'from "../../services/', to: 'from "../../../../services/' },

  // Import statements without 'from'
  { from: "import KPICard from '../../components/common/KPICard'", to: "import { KPICard } from '../../../common/KPICard'" },
  { from: "import InsightCard from '../../components/common/InsightCard'", to: "import { InsightCard } from '../../../common/InsightCard'" },
  { from: "import OnboardingTour from '../../components/common/OnboardingTour'", to: "import OnboardingTour from '../../../common/OnboardingTour'" },
  { from: "import InteractiveKPICard from '../../components/kpi/InteractiveKPICard'", to: "import InteractiveKPICard from '../../../kpi/InteractiveKPICard'" },
  { from: "import KPIDetailDrawer, { KPIDetailItem } from '../../components/kpi/KPIDetailDrawer'", to: "import KPIDetailDrawer, { KPIDetailItem } from '../../../kpi/KPIDetailDrawer'" },
  { from: "import API_CONFIG from '../../config/api'", to: "import API_CONFIG from '../../../../config/api'" },
];

// Function to fix imports in a file
function fixImportsInFile(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    let modified = false;

    for (const mapping of importMappings) {
      if (content.includes(mapping.from)) {
        content = content.split(mapping.from).join(mapping.to);
        modified = true;
      }
    }

    if (modified) {
      fs.writeFileSync(filePath, content, 'utf8');
      console.log(`✅ Fixed: ${path.relative(process.cwd(), filePath)}`);
      return true;
    }
    return false;
  } catch (error) {
    console.error(`❌ Error fixing ${filePath}:`, error.message);
    return false;
  }
}

// Function to process all .tsx files in a directory
function processDirectory(dir) {
  const files = fs.readdirSync(dir);
  let fixedCount = 0;

  for (const file of files) {
    const fullPath = path.join(dir, file);
    const stat = fs.statSync(fullPath);

    if (stat.isDirectory()) {
      fixedCount += processDirectory(fullPath);
    } else if (file.endsWith('.tsx')) {
      if (fixImportsInFile(fullPath)) {
        fixedCount++;
      }
    }
  }

  return fixedCount;
}

// Main execution
console.log('🔧 Fixing import paths in all agent dashboards...\n');

if (!fs.existsSync(agentsDir)) {
  console.error(`❌ Directory not found: ${agentsDir}`);
  process.exit(1);
}

const fixedCount = processDirectory(agentsDir);

console.log(`\n✅ Done! Fixed ${fixedCount} files.`);
