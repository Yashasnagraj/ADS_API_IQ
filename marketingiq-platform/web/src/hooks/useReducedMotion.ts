import { useEffect, useState } from 'react';

/**
 * Hook to detect if user prefers reduced motion
 * Respects system accessibility settings
 *
 * @returns boolean - true if user prefers reduced motion
 */
export const useReducedMotion = (): boolean => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    // Check if browser supports matchMedia
    if (typeof window === 'undefined' || !window.matchMedia) {
      return;
    }

    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

    // Set initial value
    setPrefersReducedMotion(mediaQuery.matches);

    // Listen for changes
    const handleChange = (event: MediaQueryListEvent) => {
      setPrefersReducedMotion(event.matches);
    };

    // Modern browsers
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
    // Legacy browsers
    else {
      mediaQuery.addListener(handleChange);
      return () => mediaQuery.removeListener(handleChange);
    }
  }, []);

  return prefersReducedMotion;
};

/**
 * Get animation configuration based on reduced motion preference
 *
 * @param normalConfig - Full animation configuration
 * @param reducedConfig - Simplified animation for reduced motion (optional)
 * @returns Appropriate animation configuration
 */
export const useAnimationConfig = <T,>(
  normalConfig: T,
  reducedConfig?: Partial<T>
): T => {
  const prefersReducedMotion = useReducedMotion();

  if (prefersReducedMotion && reducedConfig) {
    return { ...normalConfig, ...reducedConfig };
  }

  return normalConfig;
};
