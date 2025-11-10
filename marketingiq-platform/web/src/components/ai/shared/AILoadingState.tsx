import React from 'react';
import { Box, CircularProgress, Typography, keyframes } from '@mui/material';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import { colors, shadows } from '../../../theme/designTokens';

interface AILoadingStateProps {
  message?: string;
  size?: 'small' | 'medium' | 'large';
  variant?: 'spinner' | 'dots' | 'pulse';
}

// Keyframes for animations
const pulse = keyframes`
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(0.95);
  }
`;

const float = keyframes`
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
`;

const dots = keyframes`
  0%, 20% {
    color: ${colors.primary.main};
    text-shadow: 0 0 0 ${colors.primary.main};
  }
  40% {
    color: ${colors.secondary.main};
    text-shadow: 0 0 10px ${colors.primary.light};
  }
  60% {
    color: ${colors.primary.main};
    text-shadow: 0 0 0 ${colors.primary.main};
  }
  80%, 100% {
    color: ${colors.primary.main};
    text-shadow: 0 0 0 ${colors.primary.main};
  }
`;

export const AILoadingState: React.FC<AILoadingStateProps> = ({
  message = 'AI is thinking...',
  size = 'medium',
  variant = 'spinner',
}) => {
  const getSize = () => {
    switch (size) {
      case 'small':
        return { spinner: 24, icon: 24, text: '0.875rem' };
      case 'large':
        return { spinner: 60, icon: 48, text: '1.125rem' };
      default:
        return { spinner: 40, icon: 32, text: '1rem' };
    }
  };

  const sizes = getSize();

  if (variant === 'dots') {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 2,
          padding: 3,
        }}
      >
        <Box sx={{ display: 'flex', gap: 1 }}>
          {[0, 1, 2].map((index) => (
            <Box
              key={index}
              sx={{
                width: 12,
                height: 12,
                borderRadius: '50%',
                background: colors.ai.gradient,
                animation: `${pulse} 1.5s ease-in-out infinite`,
                animationDelay: `${index * 0.2}s`,
              }}
            />
          ))}
        </Box>
        <Typography
          sx={{
            fontSize: sizes.text,
            color: colors.text.secondary,
            fontWeight: 500,
          }}
        >
          {message}
        </Typography>
      </Box>
    );
  }

  if (variant === 'pulse') {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 2,
          padding: 3,
        }}
      >
        <Box
          sx={{
            width: sizes.icon,
            height: sizes.icon,
            borderRadius: 2,
            background: colors.ai.gradient,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            animation: `${pulse} 2s ease-in-out infinite`,
            boxShadow: shadows.aiGlow,
          }}
        >
          <AutoAwesomeIcon
            sx={{
              fontSize: sizes.icon * 0.6,
              color: 'white',
            }}
          />
        </Box>
        <Typography
          sx={{
            fontSize: sizes.text,
            color: colors.text.secondary,
            fontWeight: 500,
          }}
        >
          {message}
        </Typography>
      </Box>
    );
  }

  // Default spinner variant
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 2,
        padding: 3,
      }}
    >
      <Box sx={{ position: 'relative', display: 'inline-flex' }}>
        <CircularProgress
          size={sizes.spinner}
          thickness={4}
          sx={{
            color: colors.primary.main,
            '& .MuiCircularProgress-circle': {
              strokeLinecap: 'round',
            },
          }}
        />
        <Box
          sx={{
            top: 0,
            left: 0,
            bottom: 0,
            right: 0,
            position: 'absolute',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            animation: `${float} 3s ease-in-out infinite`,
          }}
        >
          <AutoAwesomeIcon
            sx={{
              fontSize: sizes.spinner * 0.5,
              color: colors.primary.main,
            }}
          />
        </Box>
      </Box>
      <Typography
        sx={{
          fontSize: sizes.text,
          color: colors.text.secondary,
          fontWeight: 500,
        }}
      >
        {message}
      </Typography>
    </Box>
  );
};

export default AILoadingState;
