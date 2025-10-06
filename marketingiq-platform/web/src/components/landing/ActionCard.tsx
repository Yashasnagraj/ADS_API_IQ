/**
 * Action Card - Prescriptive Analytics
 * Shows AI recommendations with one-click actions
 * Impact preview and apply buttons
 */
import React, { useState } from 'react';
import { Box, Card, Typography, Button, Chip, LinearProgress, useTheme, alpha } from '@mui/material';
import { keyframes } from '@mui/system';
import {
  PlayArrow,
  Pause,
  TrendingUp,
  Warning,
  CheckCircle,
  AutoAwesome,
  ElectricBolt,
} from '@mui/icons-material';
import { formatCurrency, formatPercentage } from '../../utils/chartHelpers';

const ripple = keyframes`
  0% {
    transform: scale(0);
    opacity: 1;
  }
  100% {
    transform: scale(4);
    opacity: 0;
  }
`;

const pulse = keyframes`
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
`;

export type ActionPriority = 'critical' | 'recommended' | 'opportunity';

interface ActionCardProps {
  priority: ActionPriority;
  title: string;
  description: string;
  impact: {
    metric: string;
    current: number;
    predicted: number;
    format?: 'currency' | 'percentage' | 'number';
  };
  confidence: number; // 0-100
  onApply?: () => void;
  applied?: boolean;
}

export const ActionCard: React.FC<ActionCardProps> = ({
  priority,
  title,
  description,
  impact,
  confidence,
  onApply,
  applied = false,
}) => {
  const theme = useTheme();
  const [isHovered, setIsHovered] = useState(false);
  const [showRipple, setShowRipple] = useState(false);

  const priorityConfig = {
    critical: {
      color: '#ff5252',
      icon: <Warning />,
      label: 'CRITICAL',
      bgGradient: 'linear-gradient(135deg, rgba(255, 82, 82, 0.1), rgba(255, 82, 82, 0.05))',
    },
    recommended: {
      color: '#ffa726',
      icon: <TrendingUp />,
      label: 'RECOMMENDED',
      bgGradient: 'linear-gradient(135deg, rgba(255, 167, 38, 0.1), rgba(255, 167, 38, 0.05))',
    },
    opportunity: {
      color: '#66bb6a',
      icon: <AutoAwesome />,
      label: 'OPPORTUNITY',
      bgGradient: 'linear-gradient(135deg, rgba(102, 187, 106, 0.1), rgba(102, 187, 106, 0.05))',
    },
  };

  const config = priorityConfig[priority];

  const formatValue = (value: number) => {
    switch (impact.format) {
      case 'currency':
        return formatCurrency(value);
      case 'percentage':
        return formatPercentage(value);
      default:
        return value.toLocaleString();
    }
  };

  const impactDelta = impact.predicted - impact.current;
  const impactPercent = ((impactDelta / impact.current) * 100).toFixed(1);
  const isPositive = impactDelta > 0;

  const handleApply = () => {
    setShowRipple(true);
    setTimeout(() => setShowRipple(false), 600);
    onApply?.();
  };

  return (
    <Card
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      sx={{
        position: 'relative',
        overflow: 'hidden',
        background: config.bgGradient,
        border: `1px solid ${alpha(config.color, 0.3)}`,
        borderRadius: 2,
        transition: 'all 0.3s ease',
        ...(priority === 'critical' && !applied && {
          animation: `${pulse} 2s ease-in-out infinite`,
        }),
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: `0 8px 24px ${alpha(config.color, 0.3)}`,
          borderColor: alpha(config.color, 0.5),
        },
      }}
    >
      {/* Ripple effect on apply */}
      {showRipple && (
        <Box
          sx={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            width: 20,
            height: 20,
            borderRadius: '50%',
            background: alpha(config.color, 0.5),
            animation: `${ripple} 0.6s ease-out`,
            transform: 'translate(-50%, -50%)',
          }}
        />
      )}

      {/* Priority badge */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          right: 0,
          background: alpha(config.color, 0.2),
          px: 1.5,
          py: 0.5,
          borderBottomLeftRadius: 8,
          display: 'flex',
          alignItems: 'center',
          gap: 0.5,
        }}
      >
        <Box sx={{ color: config.color, fontSize: '0.9rem', display: 'flex' }}>
          {config.icon}
        </Box>
        <Typography
          variant="caption"
          sx={{
            color: config.color,
            fontWeight: 700,
            fontSize: '0.65rem',
            letterSpacing: 0.5,
          }}
        >
          {config.label}
        </Typography>
      </Box>

      <Box sx={{ p: 2.5, pt: 4 }}>
        {/* Title */}
        <Typography
          variant="h6"
          sx={{
            fontWeight: 600,
            color: theme.palette.text.primary,
            mb: 1,
            fontSize: '1rem',
          }}
        >
          {title}
        </Typography>

        {/* Description */}
        <Typography
          variant="body2"
          sx={{
            color: theme.palette.text.secondary,
            mb: 2,
            fontSize: '0.85rem',
            lineHeight: 1.5,
          }}
        >
          {description}
        </Typography>

        {/* Impact preview */}
        <Box
          sx={{
            background: alpha(theme.palette.background.paper, 0.5),
            borderRadius: 1.5,
            p: 1.5,
            mb: 2,
            border: `1px solid ${alpha(config.color, 0.2)}`,
          }}
        >
          <Typography
            variant="caption"
            sx={{
              color: theme.palette.text.secondary,
              textTransform: 'uppercase',
              fontSize: '0.65rem',
              letterSpacing: 0.5,
              display: 'block',
              mb: 1,
            }}
          >
            Predicted Impact on {impact.metric}
          </Typography>

          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
            <Box>
              <Typography variant="caption" sx={{ color: theme.palette.text.secondary, fontSize: '0.7rem' }}>
                Current
              </Typography>
              <Typography variant="body2" sx={{ color: theme.palette.text.primary, fontWeight: 600 }}>
                {formatValue(impact.current)}
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <Typography
                variant="h6"
                sx={{
                  color: isPositive ? '#66bb6a' : '#ff5252',
                  fontWeight: 700,
                  fontSize: '1.1rem',
                }}
              >
                {isPositive ? '↑' : '↓'} {impactPercent}%
              </Typography>
            </Box>

            <Box>
              <Typography variant="caption" sx={{ color: theme.palette.text.secondary, fontSize: '0.7rem' }}>
                Predicted
              </Typography>
              <Typography
                variant="body2"
                sx={{
                  color: isPositive ? '#66bb6a' : '#ff5252',
                  fontWeight: 700,
                }}
              >
                {formatValue(impact.predicted)}
              </Typography>
            </Box>
          </Box>

          {/* Progress bar visualization */}
          <Box sx={{ position: 'relative', height: 6, background: alpha('#fff', 0.1), borderRadius: 3, overflow: 'hidden' }}>
            <Box
              sx={{
                position: 'absolute',
                left: 0,
                top: 0,
                height: '100%',
                width: `${Math.min((impact.predicted / Math.max(impact.current, impact.predicted)) * 100, 100)}%`,
                background: `linear-gradient(90deg, ${config.color}, ${alpha(config.color, 0.6)})`,
                borderRadius: 3,
                transition: 'width 0.5s ease-out',
              }}
            />
          </Box>
        </Box>

        {/* Confidence indicator */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <ElectricBolt sx={{ fontSize: '1rem', color: '#ffa726' }} />
          <Typography variant="caption" sx={{ color: theme.palette.text.secondary, fontSize: '0.7rem' }}>
            AI Confidence:
          </Typography>
          <Chip
            label={`${confidence}%`}
            size="small"
            sx={{
              height: 20,
              fontSize: '0.7rem',
              fontWeight: 700,
              background: alpha('#ffa726', 0.15),
              color: '#ffa726',
            }}
          />
        </Box>

        {/* Action button */}
        {applied ? (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              justifyContent: 'center',
              py: 1,
              background: alpha('#66bb6a', 0.15),
              borderRadius: 1,
              border: `1px solid ${alpha('#66bb6a', 0.3)}`,
            }}
          >
            <CheckCircle sx={{ fontSize: '1.2rem', color: '#66bb6a' }} />
            <Typography variant="body2" sx={{ color: '#66bb6a', fontWeight: 600 }}>
              Applied Successfully
            </Typography>
          </Box>
        ) : (
          <Button
            variant="contained"
            fullWidth
            onClick={handleApply}
            sx={{
              background: `linear-gradient(135deg, ${config.color}, ${alpha(config.color, 0.8)})`,
              color: '#fff',
              fontWeight: 700,
              py: 1,
              textTransform: 'none',
              boxShadow: `0 4px 12px ${alpha(config.color, 0.3)}`,
              '&:hover': {
                background: `linear-gradient(135deg, ${alpha(config.color, 0.9)}, ${config.color})`,
                boxShadow: `0 6px 16px ${alpha(config.color, 0.4)}`,
                transform: 'scale(1.02)',
              },
              transition: 'all 0.2s ease',
            }}
            startIcon={<PlayArrow />}
          >
            Apply Recommendation
          </Button>
        )}
      </Box>
    </Card>
  );
};

export default ActionCard;
