/**
 * Data Quality Indicator - Shows data freshness and health
 *
 * Displays across all dashboards to build trust in data
 */

import React from 'react';
import {
  Box,
  Chip,
  Tooltip,
  Typography,
  LinearProgress,
  Stack,
} from '@mui/material';
import {
  CheckCircle,
  Warning,
  Sync,
  Schedule,
  Speed,
} from '@mui/icons-material';

interface DataQualityIndicatorProps {
  lastSync?: Date | string;
  dataPoints?: number;
  qualityScore?: number;
  isLoading?: boolean;
  compact?: boolean;
}

export const DataQualityIndicator: React.FC<DataQualityIndicatorProps> = ({
  lastSync,
  dataPoints = 0,
  qualityScore = 85,
  isLoading = false,
  compact = false,
}) => {
  const getTimeAgo = (date: Date | string) => {
    const now = new Date();
    const syncDate = typeof date === 'string' ? new Date(date) : date;
    const diffMs = now.getTime() - syncDate.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  const getQualityConfig = (score: number) => {
    if (score >= 90) {
      return {
        color: '#10b981',
        label: 'Excellent',
        icon: <CheckCircle sx={{ fontSize: 16 }} />,
      };
    }
    if (score >= 75) {
      return {
        color: '#3b82f6',
        label: 'Good',
        icon: <CheckCircle sx={{ fontSize: 16 }} />,
      };
    }
    if (score >= 60) {
      return {
        color: '#f59e0b',
        label: 'Fair',
        icon: <Warning sx={{ fontSize: 16 }} />,
      };
    }
    return {
      color: '#ef4444',
      label: 'Poor',
      icon: <Warning sx={{ fontSize: 16 }} />,
    };
  };

  const qualityConfig = getQualityConfig(qualityScore);

  if (compact) {
    return (
      <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
        <Tooltip title={`Last synced: ${lastSync ? getTimeAgo(lastSync) : 'Unknown'}`}>
          <Chip
            icon={<Sync sx={{ fontSize: 14 }} />}
            label={lastSync ? getTimeAgo(lastSync) : 'No sync'}
            size="small"
            sx={{
              bgcolor: 'background.paper',
              border: '1px solid',
              borderColor: 'divider',
              fontSize: '0.75rem',
              fontWeight: 600,
            }}
          />
        </Tooltip>
        <Tooltip title={`Data Quality: ${qualityScore}%`}>
          <Chip
            icon={qualityConfig.icon}
            label={`${qualityScore}%`}
            size="small"
            sx={{
              bgcolor: `${qualityConfig.color}10`,
              color: qualityConfig.color,
              border: `1px solid ${qualityConfig.color}`,
              fontSize: '0.75rem',
              fontWeight: 600,
            }}
          />
        </Tooltip>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        p: 2,
        bgcolor: 'background.paper',
        borderRadius: 2,
        border: '1px solid',
        borderColor: 'divider',
      }}
    >
      <Stack spacing={2}>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="subtitle2" fontWeight={700} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Speed fontSize="small" color="primary" />
            Data Quality
          </Typography>
          <Chip
            icon={qualityConfig.icon}
            label={qualityConfig.label}
            size="small"
            sx={{
              bgcolor: `${qualityConfig.color}10`,
              color: qualityConfig.color,
              border: `1px solid ${qualityConfig.color}`,
              fontWeight: 600,
            }}
          />
        </Box>

        {/* Quality Score */}
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="caption" color="text.secondary">
              Quality Score
            </Typography>
            <Typography variant="caption" fontWeight={700} sx={{ color: qualityConfig.color }}>
              {qualityScore}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={qualityScore}
            sx={{
              height: 6,
              borderRadius: 3,
              bgcolor: `${qualityConfig.color}15`,
              '& .MuiLinearProgress-bar': {
                bgcolor: qualityConfig.color,
                borderRadius: 3,
              },
            }}
          />
        </Box>

        {/* Stats */}
        <Stack direction="row" spacing={2}>
          <Tooltip title="Time since last data sync">
            <Box sx={{ flex: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                <Schedule sx={{ fontSize: 14, color: 'text.secondary' }} />
                <Typography variant="caption" color="text.secondary">
                  Last Sync
                </Typography>
              </Box>
              <Typography variant="body2" fontWeight={700}>
                {lastSync ? getTimeAgo(lastSync) : 'Not synced'}
              </Typography>
            </Box>
          </Tooltip>

          <Tooltip title="Number of data points analyzed">
            <Box sx={{ flex: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                <CheckCircle sx={{ fontSize: 14, color: 'text.secondary' }} />
                <Typography variant="caption" color="text.secondary">
                  Data Points
                </Typography>
              </Box>
              <Typography variant="body2" fontWeight={700}>
                {dataPoints.toLocaleString()}
              </Typography>
            </Box>
          </Tooltip>
        </Stack>

        {/* Loading indicator */}
        {isLoading && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Sync sx={{ fontSize: 16, color: 'primary.main', animation: 'spin 1s linear infinite' }} />
            <Typography variant="caption" color="primary">
              Syncing data...
            </Typography>
          </Box>
        )}
      </Stack>

      <style>
        {`
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}
      </style>
    </Box>
  );
};
