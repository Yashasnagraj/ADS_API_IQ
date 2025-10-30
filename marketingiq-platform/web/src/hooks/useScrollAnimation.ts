import { useEffect, useState, RefObject } from 'react';
import { useScroll, useTransform, MotionValue } from 'framer-motion';

/**
 * Hook to detect if an element is in viewport
 *
 * @param ref - Reference to the element to observe
 * @param options - Intersection Observer options
 * @returns boolean indicating if element is in viewport
 */
export const useInView = (
  ref: RefObject<Element>,
  options: IntersectionObserverInit = {}
): boolean => {
  const [isInView, setIsInView] = useState(false);

  useEffect(() => {
    if (!ref.current) return;

    const observer = new IntersectionObserver(([entry]) => {
      setIsInView(entry.isIntersecting);
    }, options);

    observer.observe(ref.current);

    return () => {
      if (ref.current) {
        observer.unobserve(ref.current);
      }
    };
  }, [ref, options]);

  return isInView;
};

/**
 * Hook to get scroll progress of a specific element
 *
 * @param ref - Reference to the element
 * @returns MotionValue representing scroll progress (0 to 1)
 */
export const useElementScrollProgress = (
  ref: RefObject<HTMLElement>
): MotionValue<number> => {
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start end', 'end start'],
  });

  return scrollYProgress;
};

/**
 * Hook to create parallax effect based on scroll
 *
 * @param ref - Reference to the element
 * @param speed - Parallax speed multiplier (negative for reverse)
 * @returns MotionValue for y position
 */
export const useParallax = (
  ref: RefObject<HTMLElement>,
  speed: number = 0.5
): MotionValue<number> => {
  const scrollYProgress = useElementScrollProgress(ref);
  return useTransform(scrollYProgress, [0, 1], [0, speed * 300]);
};

/**
 * Hook to get scroll velocity
 *
 * @returns Current scroll velocity
 */
export const useScrollVelocity = (): number => {
  const [velocity, setVelocity] = useState(0);
  const [lastScrollY, setLastScrollY] = useState(0);
  const [lastTimestamp, setLastTimestamp] = useState(Date.now());

  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      const currentTimestamp = Date.now();

      const distance = currentScrollY - lastScrollY;
      const time = currentTimestamp - lastTimestamp;

      const newVelocity = time > 0 ? distance / time : 0;

      setVelocity(newVelocity);
      setLastScrollY(currentScrollY);
      setLastTimestamp(currentTimestamp);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [lastScrollY, lastTimestamp]);

  return velocity;
};

/**
 * Hook to detect scroll direction
 *
 * @returns 'up', 'down', or null
 */
export const useScrollDirection = (): 'up' | 'down' | null => {
  const [scrollDirection, setScrollDirection] = useState<'up' | 'down' | null>(null);
  const [lastScrollY, setLastScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY;

      if (currentScrollY > lastScrollY) {
        setScrollDirection('down');
      } else if (currentScrollY < lastScrollY) {
        setScrollDirection('up');
      }

      setLastScrollY(currentScrollY);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [lastScrollY]);

  return scrollDirection;
};

/**
 * Hook for smooth scroll to element
 *
 * @returns Function to scroll to element smoothly
 */
export const useSmoothScroll = () => {
  const scrollToElement = (elementId: string, offset: number = 0) => {
    const element = document.getElementById(elementId);
    if (!element) return;

    const elementPosition = element.getBoundingClientRect().top + window.scrollY;
    const offsetPosition = elementPosition - offset;

    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth',
    });
  };

  return { scrollToElement };
};

/**
 * Hook to create fade-in effect based on scroll position
 *
 * @param ref - Reference to the element
 * @returns MotionValue for opacity
 */
export const useScrollFadeIn = (ref: RefObject<HTMLElement>): MotionValue<number> => {
  const scrollYProgress = useElementScrollProgress(ref);
  return useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [0, 1, 1, 0]);
};

/**
 * Hook to create scale effect based on scroll position
 *
 * @param ref - Reference to the element
 * @param startScale - Initial scale value
 * @param endScale - Final scale value
 * @returns MotionValue for scale
 */
export const useScrollScale = (
  ref: RefObject<HTMLElement>,
  startScale: number = 0.8,
  endScale: number = 1
): MotionValue<number> => {
  const scrollYProgress = useElementScrollProgress(ref);
  return useTransform(scrollYProgress, [0, 0.5], [startScale, endScale]);
};

/**
 * Hook to track current section based on scroll position
 *
 * @param sectionIds - Array of section IDs to track
 * @returns Current active section ID
 */
export const useActiveSection = (sectionIds: string[]): string | null => {
  const [activeSection, setActiveSection] = useState<string | null>(null);

  useEffect(() => {
    const handleScroll = () => {
      const scrollPosition = window.scrollY + window.innerHeight / 2;

      for (const sectionId of sectionIds) {
        const element = document.getElementById(sectionId);
        if (!element) continue;

        const { offsetTop, offsetHeight } = element;

        if (
          scrollPosition >= offsetTop &&
          scrollPosition < offsetTop + offsetHeight
        ) {
          setActiveSection(sectionId);
          break;
        }
      }
    };

    handleScroll(); // Initial check
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [sectionIds]);

  return activeSection;
};
