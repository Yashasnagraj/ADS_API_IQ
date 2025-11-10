import React from 'react';
import { Box, Typography, LinearProgress, Tooltip } from '@mui/material';
import { colors } from '../../../theme/designTokens';

interface ConfidenceScoreProps {
  score: number; // 0-100
  label?: string;
  showPercentage?: boolean;
  size?: 'small' | 'medium' | 'large';
  variant?: 'default' | 'compact';
}

export const ConfidenceScore: React.FC<ConfidenceScoreProps> = ({
  score,
  label = 'Confidence',
  showPercentage = true,
  size = 'medium',
  variant = 'default',
}) => {
  // Determine color based on confidence score
  const getColor = (value: number) => {
    if (value >= 80) return colors.success.main;
    if (value >= 60) return colors.info.main;
    if (value >= 40) return colors.warning.main;
    return colors.error.main;
  };

  // Get size dimensions
  const getSizeDimensions = () => {
    switch (size) {
      case 'small':
        return { width: 60, height: 4, fontSize: '0.75rem' };
      case 'large':
        return { width: 150, height: 8, fontSize: '1rem' };
      default:
        return { width: 100, height: 6, fontSize: '0.875rem' };
    }
  };

  const dimensions = getSizeDimensions();
  const barColor = getColor(score);

  if (variant === 'compact') {
    return (
      <Tooltip title={`${label}: ${score}%`} arrow>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <LinearProgress
            variant="determinate"
            value={score}
            sx={{
              width: dimensions.width,
              height: dimensions.height,
              borderRadius: 3,
              bgcolor: `${barColor}20`,
              '& .MuiLinearProgress-bar': {
                bgcolor: barColor,
                borderRadius: 3,
              },
            }}
          />
          {showPercentage && (
            <Typography
              variant="body2"
              sx={{
                fontSize: dimensions.fontSize,
                fontWeight: 600,
                color: barColor,
                minWidth: '35px',
              }}
            >
              {score}%
            </Typography>
          )}
        </Box>
      </Tooltip>
    );
  }

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      <Typography
        variant="body2"
        sx={{
          fontSize: dimensions.fontSize,
          color: colors.text.secondary,
          whiteSpace: 'nowrap',
        }}
      >
        {label}:
      </Typography>
      <LinearProgress
        variant="determinate"
        value={score}
        sx={{
          width: dimensions.width,
          height: dimensions.height,
          borderRadius: 3,
          bgcolor: `${barColor}20`,
          '& .MuiLinearProgress-bar': {
            bgcolor: barColor,
            borderRadius: 3,
            transition: 'all 0.5s ease',
          },
        }}
      />
      {showPercentage && (
        <Typography
          variant="body2"
          sx={{
            fontSize: dimensions.fontSize,
            fontWeight: 600,
            color: barColor,
            minWidth: '35px',
          }}
        >
          {score}%
        </Typography>
      )}
    </Box>
  );
};

export default ConfidenceScore;
