import React, { ReactNode } from 'react';
import { Grid, Box, Fade } from '@mui/material';
import DashboardTemplate from '../common/DashboardTemplate';
import { GlobalFilterBar } from '../common/GlobalFilterBar';
import InteractiveKPICard from '../kpi/InteractiveKPICard';
import KPIDetailDrawer, { KPIDetailItem } from '../kpi/KPIDetailDrawer';
import AIIntelligenceSection, { AIInsight } from '../common/AIIntelligenceSection';
import { FilterState } from '../../types';

export interface KPIConfig {
  title: string;
  value: number;
  format?: 'number' | 'currency' | 'percentage';
  icon: ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: number;
  color?: 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info';
  onClick?: () => void;
  drillDownAvailable?: boolean;
}

export interface AgentDashboardLayoutProps {
  title: string;
  subtitle: string;
  kpis: KPIConfig[];
  aiInsights?: AIInsight[];
  children?: ReactNode;
  loading?: boolean;
  filters?: FilterState;
  onFilterChange?: (filters: FilterState) => void;
  showPlatformFilter?: boolean;
  drawerOpen?: boolean;
  drawerTitle?: string;
  drawerSubtitle?: string;
  drawerData?: KPIDetailItem[];
  onDrawerClose?: () => void;
  selectedTimeRange?: string;
  onTimeRangeChange?: () => void;
}

/**
 * Standard layout component for all agent dashboards
 * Follows the InsightsSummary design pattern with:
 * - Interactive KPI Cards (6 cards in a row)
 * - AI Intelligence Section (premium insights display)
 * - Enhanced Charts and data visualizations
 * - KPI Detail Drawer for drill-down
 */
export const AgentDashboardLayout: React.FC<AgentDashboardLayoutProps> = ({
  title,
  subtitle,
  kpis,
  aiInsights,
  children,
  loading = false,
  filters,
  onFilterChange,
  showPlatformFilter = false,
  drawerOpen = false,
  drawerTitle = '',
  drawerSubtitle = '',
  drawerData = [],
  onDrawerClose,
  selectedTimeRange,
  onTimeRangeChange,
}) => {
  return (
    <DashboardTemplate
      title={title}
      subtitle={subtitle}
      selectedTimeRange={selectedTimeRange}
      onTimeRangeChange={onTimeRangeChange}
    >
      {/* Global Filter Bar */}
      {onFilterChange && (
        <GlobalFilterBar
          onFilterChange={onFilterChange}
          showPlatformFilter={showPlatformFilter}
        />
      )}

      {/* Interactive KPI Cards Grid - 6 cards per row */}
      <Grid container spacing={3} sx={{ mb: 3, mt: onFilterChange ? 0 : 2 }}>
        {kpis.map((kpi, index) => (
          <Grid item xs={12} sm={6} md={2} key={index}>
            <InteractiveKPICard
              title={kpi.title}
              value={kpi.value}
              format={kpi.format || 'number'}
              icon={kpi.icon}
              trend={kpi.trend || 'neutral'}
              trendValue={kpi.trendValue || 0}
              color={kpi.color || 'primary'}
              index={index}
              onClick={kpi.onClick}
              drillDownAvailable={kpi.drillDownAvailable}
            />
          </Grid>
        ))}
      </Grid>

      {/* AI Intelligence Section - Premium insights display */}
      {aiInsights && aiInsights.length > 0 && (
        <Box sx={{ mb: 3 }}>
          <AIIntelligenceSection insights={aiInsights} />
        </Box>
      )}

      {/* Custom Chart and Data Content */}
      {children && (
        <Fade in timeout={600}>
          <Box>{children}</Box>
        </Fade>
      )}

      {/* KPI Detail Drawer - Drill-down for detailed data */}
      {onDrawerClose && (
        <KPIDetailDrawer
          open={drawerOpen}
          onClose={onDrawerClose}
          title={drawerTitle}
          subtitle={drawerSubtitle}
          data={drawerData}
        />
      )}
    </DashboardTemplate>
  );
};

export default AgentDashboardLayout;
