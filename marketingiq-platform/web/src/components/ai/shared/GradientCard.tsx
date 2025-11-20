import React from 'react';
import { Card, CardProps, Box } from '@mui/material';
import { colors, shadows } from '../../../theme/designTokens';

interface GradientCardProps extends CardProps {
  children: React.ReactNode;
  variant?: 'ai' | 'success' | 'warning' | 'error' | 'info';
  intensity?: 'subtle' | 'medium' | 'strong';
  glow?: boolean;
}

export const GradientCard: React.FC<GradientCardProps> = ({
  children,
  variant = 'ai',
  intensity = 'medium',
  glow = false,
  sx,
  ...props
}) => {
  // Get gradient based on variant
  const getGradient = () => {
    switch (variant) {
      case 'success':
        return `linear-gradient(135deg, ${colors.success.light} 0%, ${colors.success.dark} 100%)`;
      case 'warning':
        return `linear-gradient(135deg, ${colors.warning.light} 0%, ${colors.warning.dark} 100%)`;
      case 'error':
        return `linear-gradient(135deg, ${colors.error.light} 0%, ${colors.error.dark} 100%)`;
      case 'info':
        return `linear-gradient(135deg, ${colors.info.light} 0%, ${colors.info.dark} 100%)`;
      default:
        return colors.ai.gradient;
    }
  };

  // Get background color with intensity
  const getBackground = () => {
    const gradient = getGradient();

    switch (intensity) {
      case 'subtle':
        return `linear-gradient(135deg, ${variant === 'ai' ? colors.primary[50] : colors[variant][50]} 0%, ${variant === 'ai' ? colors.secondary[50] : colors[variant][100]} 100%)`;
      case 'strong':
        return gradient;
      default: // medium
        return variant === 'ai'
          ? `linear-gradient(135deg, ${colors.primary[100]} 0%, ${colors.secondary[100]} 100%)`
          : `linear-gradient(135deg, ${colors[variant][100]} 0%, ${colors[variant][200]} 100%)`;
    }
  };

  // Get border color
  const getBorderColor = () => {
    switch (variant) {
      case 'success':
        return colors.success.main;
      case 'warning':
        return colors.warning.main;
      case 'error':
        return colors.error.main;
      case 'info':
        return colors.info.main;
      default:
        return colors.primary.main;
    }
  };

  const background = getBackground();
  const borderColor = getBorderColor();

  return (
    <Card
      sx={{
        background: intensity === 'strong' ? background : 'white',
        borderRadius: 2,
        border: intensity === 'strong' ? 'none' : `2px solid ${borderColor}`,
        boxShadow: glow ? shadows.aiGlow : shadows.md,
        position: 'relative',
        overflow: 'visible',
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: glow ? shadows.aiGlowStrong : shadows.lg,
        },
        ...sx,
      }}
      {...props}
    >
      {intensity !== 'strong' && (
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '4px',
            background: getGradient(),
            borderTopLeftRadius: '8px',
            borderTopRightRadius: '8px',
          }}
        />
      )}
      {children}
    </Card>
  );
};

export default GradientCard;
