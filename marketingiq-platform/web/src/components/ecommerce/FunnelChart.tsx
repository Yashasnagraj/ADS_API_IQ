/**
 * Funnel Chart Component
 * Displays conversion funnel with drop-off percentages
 */
import React from 'react';
import { Box, Typography, Tooltip, useTheme, alpha } from '@mui/material';
import { Warning, CheckCircle, Info } from '@mui/icons-material';

interface FunnelStage {
  stage: string;
  value: number;
  percentage: number;
  dropoff: number;
  insight?: string;
}

interface FunnelChartProps {
  data: {
    stages: FunnelStage[];
    overall_conversion_rate: number;
  } | null;
}

export const FunnelChart: React.FC<FunnelChartProps> = ({ data }) => {
  const theme = useTheme();

  if (!data || !data.stages) {
    return <Typography>No funnel data available</Typography>;
  }

  const { stages, overall_conversion_rate } = data;
  const maxValue = stages[0]?.value || 1;

  const getDropoffColor = (dropoff: number) => {
    if (dropoff > 40) return '#ef4444'; // Critical
    if (dropoff > 20) return '#f59e0b'; // Warning
    return '#10b981'; // Healthy
  };

  const getDropoffIcon = (dropoff: number) => {
    if (dropoff > 40) return <Warning sx={{ fontSize: '1rem' }} />;
    if (dropoff > 20) return <Info sx={{ fontSize: '1rem' }} />;
    return <CheckCircle sx={{ fontSize: '1rem' }} />;
  };

  return (
    <Box>
      {/* Overall CVR */}
      <Box sx={{ mb: 3, textAlign: 'center' }}>
        <Typography variant="body2" sx={{ color: theme.palette.text.secondary, mb: 0.5 }}>
          Overall Conversion Rate
        </Typography>
        <Typography variant="h4" sx={{ fontWeight: 700, color: theme.palette.primary.main }}>
          {overall_conversion_rate.toFixed(2)}%
        </Typography>
      </Box>

      {/* Funnel Stages */}
      <Box sx={{ position: 'relative' }}>
        {stages.map((stage, index) => {
          const widthPercentage = (stage.value / maxValue) * 100;
          const dropoffColor = getDropoffColor(stage.dropoff);

          return (
            <Tooltip
              key={index}
              title={stage.insight || `${stage.value.toLocaleString()} ${stage.stage.toLowerCase()}`}
              arrow
            >
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    {stage.stage}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {index > 0 && (
                      <Box
                        sx={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 0.5,
                          px: 1,
                          py: 0.3,
                          borderRadius: 1,
                          background: alpha(dropoffColor, 0.1),
                          color: dropoffColor
                        }}
                      >
                        {getDropoffIcon(stage.dropoff)}
                        <Typography variant="caption" sx={{ fontWeight: 600 }}>
                          -{stage.dropoff.toFixed(1)}%
                        </Typography>
                      </Box>
                    )}
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {stage.value.toLocaleString()}
                    </Typography>
                  </Box>
                </Box>

                {/* Funnel bar */}
                <Box
                  sx={{
                    width: `${widthPercentage}%`,
                    height: 48,
                    background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
                    borderRadius: 1,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    position: 'relative',
                    boxShadow: `0 4px 12px ${alpha(theme.palette.primary.main, 0.3)}`,
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'scale(1.02)',
                      boxShadow: `0 6px 16px ${alpha(theme.palette.primary.main, 0.4)}`
                    }
                  }}
                >
                  <Typography variant="body2" sx={{ color: 'white', fontWeight: 600 }}>
                    {stage.percentage.toFixed(1)}%
                  </Typography>
                </Box>
              </Box>
            </Tooltip>
          );
        })}
      </Box>
    </Box>
  );
};

export default FunnelChart;
