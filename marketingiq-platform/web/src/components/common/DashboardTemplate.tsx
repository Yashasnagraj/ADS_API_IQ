import React, { ReactNode } from 'react';
import {
  Box,
  Typography,
  Chip,
  IconButton,
  Stack,
  Fade,
  Avatar,
} from '@mui/material';
import {
  Schedule,
  Refresh,
  Download,
  Share,
  Psychology,
} from '@mui/icons-material';
import { keyframes } from '@mui/system';
import { useTheme } from '@mui/material';

// Shared animations
export const animations = {
  pulse: keyframes`
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
  `,
  shimmer: keyframes`
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
  `,
  fadeInUp: keyframes`
    from {
      opacity: 0;
      transform: translateY(30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  `,
  glow: keyframes`
    0%, 100% {
      box-shadow: 0 0 20px rgba(99, 102, 241, 0.3);
    }
    50% {
      box-shadow: 0 0 40px rgba(99, 102, 241, 0.6);
    }
  `,
  float: keyframes`
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
  `,
};

interface DashboardTemplateProps {
  title: string;
  subtitle: string;
  selectedTimeRange?: string;
  onTimeRangeChange?: () => void;
  children: ReactNode;
  showAIBadge?: boolean;
}

const DashboardTemplate: React.FC<DashboardTemplateProps> = ({
  title,
  subtitle,
  selectedTimeRange,
  onTimeRangeChange,
  children,
  showAIBadge = true,
}) => {
  const theme = useTheme();

  return (
    <Box sx={{ p: 3 }}>
      {/* Header Section */}
      <Fade in timeout={600}>
        <Box sx={{ mb: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Box display="flex" alignItems="center" gap={2}>
              {showAIBadge && (
                <Avatar
                  sx={{
                    bgcolor: theme.palette.primary.main,
                    width: 40,
                    height: 40,
                    animation: `${animations.float} 3s ease-in-out infinite`,
                  }}
                >
                  <Psychology />
                </Avatar>
              )}
              <Box>
                <Typography variant="h4" fontWeight="bold" gutterBottom>
                  {title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {subtitle}
                </Typography>
              </Box>
            </Box>
            <Stack direction="row" spacing={1}>
              <Chip
                icon={<Schedule fontSize="small" />}
                label={selectedTimeRange === '7d' ? 'Last 7 Days' : 'Last 30 Days'}
                onClick={onTimeRangeChange}
                color="primary"
                variant="outlined"
                size="small"
              />
              <IconButton size="small" color="primary">
                <Refresh fontSize="small" />
              </IconButton>
              <IconButton size="small" color="primary">
                <Download fontSize="small" />
              </IconButton>
              <IconButton size="small" color="primary">
                <Share fontSize="small" />
              </IconButton>
            </Stack>
          </Box>
        </Box>
      </Fade>

      {/* Main Content */}
      {children}
    </Box>
  );
};

export default DashboardTemplate;

// Export shared utilities
export const formatCompactNumber = (num: number): string => {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
  return num.toString();
};

export const getPriorityColor = (priority: string, theme: any): string => {
  switch (priority) {
    case 'high':
      return theme.palette.error.main;
    case 'medium':
      return theme.palette.warning.main;
    case 'low':
      return theme.palette.success.main;
    default:
      return theme.palette.text.secondary;
  }
};
