import React, { useRef } from 'react';
import { motion } from 'framer-motion';
import { Button, ButtonProps } from '@mui/material';
import { useMagneticEffect } from '../../../hooks/useMousePosition';
import { useReducedMotion } from '../../../hooks/useReducedMotion';

interface MagneticButtonProps extends ButtonProps {
  magneticStrength?: number; // 0-1, how strong the magnetic effect is
  magneticRange?: number; // Detection range in pixels
  glowEffect?: boolean; // Add glow on hover
}

/**
 * Button with magnetic effect - follows cursor when nearby
 * Includes optional glow pulse animation
 */
const MagneticButton: React.FC<MagneticButtonProps> = ({
  children,
  magneticStrength = 0.3,
  magneticRange = 200,
  glowEffect = true,
  ...buttonProps
}) => {
  const buttonRef = useRef<HTMLButtonElement>(null);
  const magneticOffset = useMagneticEffect(buttonRef, magneticStrength, magneticRange);
  const prefersReducedMotion = useReducedMotion();

  // Disable magnetic effect for reduced motion
  const x = prefersReducedMotion ? 0 : magneticOffset.x;
  const y = prefersReducedMotion ? 0 : magneticOffset.y;

  return (
    <motion.div
      style={{
        display: 'inline-block',
        x,
        y,
      }}
      transition={{
        type: 'spring',
        stiffness: 150,
        damping: 15,
        mass: 0.1,
      }}
    >
      <Button
        ref={buttonRef}
        {...buttonProps}
        sx={{
          position: 'relative',
          overflow: 'hidden',
          ...buttonProps.sx,
          '&::before': glowEffect
            ? {
                content: '""',
                position: 'absolute',
                top: '50%',
                left: '50%',
                width: '100%',
                height: '100%',
                background: 'radial-gradient(circle, rgba(30, 136, 229, 0.4) 0%, transparent 70%)',
                transform: 'translate(-50%, -50%) scale(0)',
                transition: 'transform 0.5s ease',
                pointerEvents: 'none',
                zIndex: 0,
              }
            : {},
          '&:hover::before': glowEffect
            ? {
                transform: 'translate(-50%, -50%) scale(2)',
              }
            : {},
          '& > *': {
            position: 'relative',
            zIndex: 1,
          },
        }}
      >
        {children}
      </Button>
    </motion.div>
  );
};

export default MagneticButton;
