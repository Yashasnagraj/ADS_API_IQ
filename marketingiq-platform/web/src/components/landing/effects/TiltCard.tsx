import React, { useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardProps } from '@mui/material';
import { useReducedMotion } from '../../../hooks/useReducedMotion';

interface TiltCardProps extends CardProps {
  tiltIntensity?: number; // 0-1, how much the card tilts
  glareEffect?: boolean; // Show light glare effect on hover
  maxTilt?: number; // Maximum tilt angle in degrees
}

/**
 * 3D tilt card that responds to mouse movement
 * Creates depth perception with transform and glare effects
 */
const TiltCard: React.FC<TiltCardProps> = ({
  children,
  tiltIntensity = 0.5,
  glareEffect = true,
  maxTilt = 15,
  ...cardProps
}) => {
  const cardRef = useRef<HTMLDivElement>(null);
  const [rotateX, setRotateX] = useState(0);
  const [rotateY, setRotateY] = useState(0);
  const [glarePosition, setGlarePosition] = useState({ x: 50, y: 50 });
  const prefersReducedMotion = useReducedMotion();

  const handleMouseMove = (event: React.MouseEvent<HTMLDivElement>) => {
    if (prefersReducedMotion || !cardRef.current) return;

    const card = cardRef.current;
    const rect = card.getBoundingClientRect();

    // Calculate mouse position relative to card center
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    const mouseX = event.clientX - centerX;
    const mouseY = event.clientY - centerY;

    // Calculate tilt angles
    const percentX = (mouseX / (rect.width / 2)) * tiltIntensity;
    const percentY = (mouseY / (rect.height / 2)) * tiltIntensity;

    setRotateY(percentX * maxTilt);
    setRotateX(-percentY * maxTilt);

    // Calculate glare position (0-100%)
    const glareX = ((event.clientX - rect.left) / rect.width) * 100;
    const glareY = ((event.clientY - rect.top) / rect.height) * 100;
    setGlarePosition({ x: glareX, y: glareY });
  };

  const handleMouseLeave = () => {
    if (prefersReducedMotion) return;
    setRotateX(0);
    setRotateY(0);
    setGlarePosition({ x: 50, y: 50 });
  };

  return (
    <motion.div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{
        perspective: 1000,
        transformStyle: 'preserve-3d',
      }}
      animate={{
        rotateX,
        rotateY,
      }}
      transition={{
        type: 'spring',
        stiffness: 300,
        damping: 30,
      }}
    >
      <Card
        {...cardProps}
        sx={{
          position: 'relative',
          overflow: 'hidden',
          transformStyle: 'preserve-3d',
          willChange: 'transform',
          ...cardProps.sx,
          '&::after': glareEffect
            ? {
                content: '""',
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                background: `radial-gradient(circle at ${glarePosition.x}% ${glarePosition.y}%, rgba(255, 255, 255, 0.3) 0%, transparent 60%)`,
                opacity: rotateX !== 0 || rotateY !== 0 ? 1 : 0,
                transition: 'opacity 0.3s ease',
                pointerEvents: 'none',
                zIndex: 10,
              }
            : {},
        }}
      >
        {children}
      </Card>
    </motion.div>
  );
};

export default TiltCard;
