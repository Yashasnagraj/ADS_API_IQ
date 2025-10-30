/**
 * Funnel Chart Component
 * Used by Google Ads, Meta Ads Manager for conversion funnels
 * Shows progression through stages (Impressions → Clicks → Conversions)
 */
import React from 'react';
import { Box, Typography, useTheme, alpha } from '@mui/material';
import { CHART_COLORS } from '../../constants/visualizations';
import { formatCompactNumber, formatPercentage } from '../../utils/chartHelpers';

export interface FunnelStage {
  name: string;
  value: number;
  color?: string;
}

interface FunnelChartProps {
  data: FunnelStage[];
  height?: number;
  showPercentages?: boolean;
  showValues?: boolean;
}

export const FunnelChart: React.FC<FunnelChartProps> = ({
  data,
  height = 400,
  showPercentages = true,
  showValues = true,
}) => {
  const theme = useTheme();

  const maxValue = Math.max(...data.map(d => d.value));
  const total = data[0]?.value || 1;

  return (
    <Box sx={{ width: '100%', height, position: 'relative' }}>
      {data.map((stage, index) => {
        const widthPercent = (stage.value / maxValue) * 100;
        const dropoff = index > 0 ? ((data[index - 1].value - stage.value) / data[index - 1].value) * 100 : 0;
        const conversionRate = (stage.value / total) * 100;
        const stageColor = stage.color || CHART_COLORS.categories[index % CHART_COLORS.categories.length];

        return (
          <Box key={index} sx={{ mb: index < data.length - 1 ? 2 : 0 }}>
            {/* Funnel Bar */}
            <Box
              sx={{
                width: `${widthPercent}%`,
                height: height / data.length - 16,
                margin: '0 auto',
                background: `linear-gradient(135deg, ${stageColor}, ${alpha(stageColor, 0.7)})`,
                borderRadius: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                px: 3,
                position: 'relative',
                boxShadow: `0 4px 12px ${alpha(stageColor, 0.3)}`,
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'scale(1.02)',
                  boxShadow: `0 6px 16px ${alpha(stageColor, 0.5)}`,
                },
              }}
            >
              <Typography
                variant="subtitle1"
                fontWeight="600"
                sx={{ color: '#fff', textShadow: '0 2px 4px rgba(0,0,0,0.3)' }}
              >
                {stage.name}
              </Typography>

              <Box sx={{ textAlign: 'right' }}>
                {showValues && (
                  <Typography
                    variant="h6"
                    fontWeight="700"
                    sx={{ color: '#fff', textShadow: '0 2px 4px rgba(0,0,0,0.3)' }}
                  >
                    {formatCompactNumber(stage.value)}
                  </Typography>
                )}
                {showPercentages && (
                  <Typography
                    variant="caption"
                    sx={{ color: alpha('#fff', 0.9), textShadow: '0 1px 2px rgba(0,0,0,0.3)' }}
                  >
                    {formatPercentage(conversionRate)}
                  </Typography>
                )}
              </Box>
            </Box>

            {/* Dropoff indicator */}
            {index < data.length - 1 && dropoff > 0 && (
              <Box sx={{ textAlign: 'center', my: 0.5 }}>
                <Typography
                  variant="caption"
                  sx={{
                    color: theme.palette.error.main,
                    fontWeight: 600,
                    fontSize: '0.7rem',
                  }}
                >
                  ↓ {formatPercentage(dropoff)} dropoff
                </Typography>
              </Box>
            )}
          </Box>
        );
      })}
    </Box>
  );
};

export default FunnelChart;
