import { Variants } from 'framer-motion';

/**
 * Animation utilities and reusable variants for MarketingIQ Landing Page
 * Optimized for 60fps performance with smooth, professional animations
 */

// Easing functions for natural motion
export const easings = {
  // Smooth ease for most animations
  smooth: [0.43, 0.13, 0.23, 0.96],
  // Bouncy for playful elements
  bouncy: [0.68, -0.55, 0.265, 1.55],
  // Sharp for quick interactions
  sharp: [0.4, 0.0, 0.2, 1],
  // Gentle for subtle movements
  gentle: [0.25, 0.46, 0.45, 0.94],
};

// Duration constants (in seconds)
export const durations = {
  fast: 0.3,
  normal: 0.5,
  slow: 0.8,
  verySlow: 1.2,
};

// ============================================
// FADE ANIMATIONS
// ============================================

export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      duration: durations.normal,
      ease: easings.smooth,
    },
  },
};

export const fadeInUp: Variants = {
  hidden: {
    opacity: 0,
    y: 60,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: durations.slow,
      ease: easings.smooth,
    },
  },
};

export const fadeInDown: Variants = {
  hidden: {
    opacity: 0,
    y: -60,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: durations.slow,
      ease: easings.smooth,
    },
  },
};

// ============================================
// SLIDE ANIMATIONS
// ============================================

export const slideInLeft: Variants = {
  hidden: {
    opacity: 0,
    x: -100,
  },
  visible: {
    opacity: 1,
    x: 0,
    transition: {
      duration: durations.slow,
      ease: easings.smooth,
    },
  },
};

export const slideInRight: Variants = {
  hidden: {
    opacity: 0,
    x: 100,
  },
  visible: {
    opacity: 1,
    x: 0,
    transition: {
      duration: durations.slow,
      ease: easings.smooth,
    },
  },
};

// ============================================
// SCALE ANIMATIONS
// ============================================

export const scaleIn: Variants = {
  hidden: {
    opacity: 0,
    scale: 0.8,
  },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: durations.slow,
      ease: easings.smooth,
    },
  },
};

export const scaleInBounce: Variants = {
  hidden: {
    opacity: 0,
    scale: 0.5,
  },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: durations.slow,
      ease: easings.bouncy,
    },
  },
};

// ============================================
// BLUR ANIMATIONS
// ============================================

export const blurIn: Variants = {
  hidden: {
    opacity: 0,
    filter: 'blur(10px)',
  },
  visible: {
    opacity: 1,
    filter: 'blur(0px)',
    transition: {
      duration: durations.slow,
      ease: easings.smooth,
    },
  },
};

export const blurInScale: Variants = {
  hidden: {
    opacity: 0,
    scale: 1.1,
    filter: 'blur(20px)',
  },
  visible: {
    opacity: 1,
    scale: 1,
    filter: 'blur(0px)',
    transition: {
      duration: durations.verySlow,
      ease: easings.smooth,
    },
  },
};

// ============================================
// ROTATE ANIMATIONS
// ============================================

export const rotateIn: Variants = {
  hidden: {
    opacity: 0,
    rotate: -180,
    scale: 0.5,
  },
  visible: {
    opacity: 1,
    rotate: 0,
    scale: 1,
    transition: {
      duration: durations.slow,
      ease: easings.smooth,
    },
  },
};

// ============================================
// STAGGER CONTAINERS
// ============================================

export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

export const staggerContainerFast: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0.1,
    },
  },
};

export const staggerContainerSlow: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2,
      delayChildren: 0.3,
    },
  },
};

// ============================================
// HOVER ANIMATIONS
// ============================================

export const hoverLift = {
  scale: 1.05,
  y: -8,
  transition: {
    duration: durations.fast,
    ease: easings.sharp,
  },
};

export const hoverScale = {
  scale: 1.1,
  transition: {
    duration: durations.fast,
    ease: easings.sharp,
  },
};

export const hoverGlow = {
  boxShadow: '0 0 20px rgba(30, 136, 229, 0.5)',
  transition: {
    duration: durations.fast,
  },
};

// ============================================
// 3D TILT EFFECT
// ============================================

export const tilt3D: Variants = {
  initial: {
    rotateX: 0,
    rotateY: 0,
  },
  hover: {
    rotateX: 10,
    rotateY: 10,
    scale: 1.05,
    transition: {
      duration: durations.fast,
      ease: easings.sharp,
    },
  },
};

// ============================================
// PULSE ANIMATIONS
// ============================================

export const pulseAnimation = {
  scale: [1, 1.05, 1],
  opacity: [0.8, 1, 0.8],
  transition: {
    duration: 2,
    repeat: Infinity,
    ease: 'easeInOut',
  },
};

export const glowPulse = {
  boxShadow: [
    '0 0 20px rgba(30, 136, 229, 0.3)',
    '0 0 40px rgba(30, 136, 229, 0.6)',
    '0 0 20px rgba(30, 136, 229, 0.3)',
  ],
  transition: {
    duration: 2,
    repeat: Infinity,
    ease: 'easeInOut',
  },
};

// ============================================
// ICON ANIMATIONS
// ============================================

export const iconFloat: Variants = {
  initial: { y: 0 },
  animate: {
    y: [-10, 10, -10],
    transition: {
      duration: 3,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

export const iconRotate: Variants = {
  initial: { rotate: 0 },
  animate: {
    rotate: 360,
    transition: {
      duration: 20,
      repeat: Infinity,
      ease: 'linear',
    },
  },
};

export const iconPulse: Variants = {
  hidden: { scale: 1 },
  visible: {
    scale: [1, 1.2, 1],
    transition: {
      duration: 1,
      repeat: 3,
      ease: easings.smooth,
    },
  },
};

// ============================================
// SCROLL-BASED ANIMATIONS
// ============================================

// For scroll-linked opacity
export const scrollFade = {
  scrollYProgress: [0, 0.5, 1],
  opacity: [0, 1, 0.8],
};

// For parallax effects
export const parallaxSlow = {
  scrollYProgress: [0, 1],
  y: [0, 200],
};

export const parallaxFast = {
  scrollYProgress: [0, 1],
  y: [0, -200],
};

// ============================================
// TYPEWRITER EFFECT
// ============================================

export const typewriterCursor: Variants = {
  initial: { opacity: 0 },
  animate: {
    opacity: [0, 1, 0],
    transition: {
      duration: 0.8,
      repeat: Infinity,
      ease: 'linear',
    },
  },
};

// ============================================
// CARD ANIMATIONS WITH DIRECTION
// ============================================

export const cardAnimation = (direction: 'left' | 'right' | 'up' | 'down', index: number): Variants => {
  const directionOffsets = {
    left: { x: -100, y: 0 },
    right: { x: 100, y: 0 },
    up: { x: 0, y: -100 },
    down: { x: 0, y: 100 },
  };

  const offset = directionOffsets[direction];

  return {
    hidden: {
      opacity: 0,
      ...offset,
      filter: 'blur(10px)',
    },
    visible: {
      opacity: 1,
      x: 0,
      y: 0,
      filter: 'blur(0px)',
      transition: {
        duration: durations.slow,
        delay: index * 0.1,
        ease: easings.smooth,
      },
    },
  };
};

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Creates a custom stagger container with configurable timing
 */
export const createStaggerContainer = (staggerDelay: number, initialDelay: number = 0): Variants => ({
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: staggerDelay,
      delayChildren: initialDelay,
    },
  },
});

/**
 * Creates a custom slide animation from any direction
 */
export const createSlideAnimation = (
  direction: 'left' | 'right' | 'up' | 'down',
  distance: number = 100,
  duration: number = durations.slow
): Variants => {
  const offsets = {
    left: { x: -distance, y: 0 },
    right: { x: distance, y: 0 },
    up: { x: 0, y: -distance },
    down: { x: 0, y: distance },
  };

  return {
    hidden: {
      opacity: 0,
      ...offsets[direction],
    },
    visible: {
      opacity: 1,
      x: 0,
      y: 0,
      transition: {
        duration,
        ease: easings.smooth,
      },
    },
  };
};

/**
 * Viewport animation configuration for optimal performance
 */
export const viewportConfig = {
  once: true, // Animate only once when entering viewport
  amount: 0.3, // Trigger when 30% visible
  margin: '0px 0px -100px 0px', // Start animation slightly before element is visible
};

/**
 * Viewport configuration for continuous animations
 */
export const viewportConfigContinuous = {
  once: false,
  amount: 0.3,
  margin: '0px 0px -100px 0px',
};
