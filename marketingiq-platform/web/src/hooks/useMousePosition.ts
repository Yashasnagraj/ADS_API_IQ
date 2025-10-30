import { useEffect, useState, RefObject } from 'react';

interface MousePosition {
  x: number;
  y: number;
}

/**
 * Hook to track mouse position globally
 *
 * @returns Current mouse position { x, y }
 */
export const useMousePosition = (): MousePosition => {
  const [mousePosition, setMousePosition] = useState<MousePosition>({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (event: MouseEvent) => {
      setMousePosition({
        x: event.clientX,
        y: event.clientY,
      });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return mousePosition;
};

/**
 * Hook to track mouse position relative to an element
 *
 * @param ref - Reference to the element
 * @returns Mouse position relative to element center { x, y }
 */
export const useMousePositionRelative = (
  ref: RefObject<HTMLElement>
): MousePosition => {
  const [relativePosition, setRelativePosition] = useState<MousePosition>({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (event: MouseEvent) => {
      if (!ref.current) return;

      const rect = ref.current.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;

      setRelativePosition({
        x: event.clientX - centerX,
        y: event.clientY - centerY,
      });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [ref]);

  return relativePosition;
};

/**
 * Hook to create magnetic effect - returns offset values when mouse is near element
 *
 * @param ref - Reference to the element
 * @param strength - Magnetic strength multiplier (0-1)
 * @param range - Detection range in pixels
 * @returns Offset values { x, y } for magnetic pull
 */
export const useMagneticEffect = (
  ref: RefObject<HTMLElement>,
  strength: number = 0.3,
  range: number = 200
): MousePosition => {
  const [offset, setOffset] = useState<MousePosition>({ x: 0, y: 0 });
  const [isHovering, setIsHovering] = useState(false);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const handleMouseMove = (event: MouseEvent) => {
      const rect = element.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;

      const deltaX = event.clientX - centerX;
      const deltaY = event.clientY - centerY;
      const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

      // Only apply magnetic effect within range
      if (distance < range) {
        const factor = isHovering ? strength * 2 : strength;
        const pullX = deltaX * factor;
        const pullY = deltaY * factor;
        setOffset({ x: pullX, y: pullY });
      } else {
        setOffset({ x: 0, y: 0 });
      }
    };

    const handleMouseEnter = () => setIsHovering(true);
    const handleMouseLeave = () => {
      setIsHovering(false);
      setOffset({ x: 0, y: 0 });
    };

    element.addEventListener('mouseenter', handleMouseEnter);
    element.addEventListener('mouseleave', handleMouseLeave);
    window.addEventListener('mousemove', handleMouseMove);

    return () => {
      element.removeEventListener('mouseenter', handleMouseEnter);
      element.removeEventListener('mouseleave', handleMouseLeave);
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, [ref, strength, range, isHovering]);

  return offset;
};

/**
 * Hook to detect hover state
 *
 * @param ref - Reference to the element
 * @returns boolean indicating hover state
 */
export const useHover = (ref: RefObject<HTMLElement>): boolean => {
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const handleMouseEnter = () => setIsHovered(true);
    const handleMouseLeave = () => setIsHovered(false);

    element.addEventListener('mouseenter', handleMouseEnter);
    element.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      element.removeEventListener('mouseenter', handleMouseEnter);
      element.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, [ref]);

  return isHovered;
};
