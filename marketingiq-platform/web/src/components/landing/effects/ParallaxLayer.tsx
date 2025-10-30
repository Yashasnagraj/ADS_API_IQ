import React, { useRef } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { Box } from '@mui/material';
import { useReducedMotion } from '../../../hooks/useReducedMotion';

interface ParallaxLayerProps {
  children: React.ReactNode;
  speed?: number; // Multiplier for parallax effect (negative for reverse)
  opacity?: [number, number]; // Opacity range [start, end]
  scale?: [number, number]; // Scale range [start, end]
  rotate?: [number, number]; // Rotation range [start, end]
  blur?: [number, number]; // Blur range [start, end] in pixels
  zIndex?: number;
  className?: string;
}

/**
 * Parallax layer component that moves at different speeds based on scroll
 * Optimized with framer-motion's useTransform for smooth 60fps animations
 */
const ParallaxLayer: React.FC<ParallaxLayerProps> = ({
  children,
  speed = 0.5,
  opacity,
  scale,
  rotate,
  blur,
  zIndex = 0,
  className,
}) => {
  const ref = useRef<HTMLDivElement>(null);
  const prefersReducedMotion = useReducedMotion();

  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start end', 'end start'],
  });

  // Calculate transform values based on scroll progress
  const y = useTransform(scrollYProgress, [0, 1], [0, speed * 300]);
  const opacityValue = opacity
    ? useTransform(scrollYProgress, [0, 0.5, 1], [opacity[0], 1, opacity[1]])
    : undefined;
  const scaleValue = scale
    ? useTransform(scrollYProgress, [0, 0.5, 1], [scale[0], 1, scale[1]])
    : undefined;
  const rotateValue = rotate
    ? useTransform(scrollYProgress, [0, 1], rotate)
    : undefined;
  const blurValue = blur
    ? useTransform(scrollYProgress, [0, 0.5, 1], [
        `blur(${blur[0]}px)`,
        'blur(0px)',
        `blur(${blur[1]}px)`,
      ])
    : undefined;

  // Disable parallax for users who prefer reduced motion
  if (prefersReducedMotion) {
    return (
      <Box
        ref={ref}
        className={className}
        sx={{
          position: 'relative',
          zIndex,
        }}
      >
        {children}
      </Box>
    );
  }

  return (
    <motion.div
      ref={ref}
      className={className}
      style={{
        y,
        opacity: opacityValue,
        scale: scaleValue,
        rotate: rotateValue,
        filter: blurValue,
        position: 'relative',
        zIndex,
        willChange: 'transform',
      }}
    >
      {children}
    </motion.div>
  );
};

export default ParallaxLayer;
