import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Typography, TypographyProps } from '@mui/material';
import { useReducedMotion } from '../../../hooks/useReducedMotion';

interface TypewriterTextProps extends Omit<TypographyProps, 'children'> {
  text: string | string[]; // Single text or array for multiple lines
  speed?: number; // Characters per second
  delay?: number; // Initial delay before typing starts
  showCursor?: boolean;
  cursorChar?: string;
  onComplete?: () => void;
  loop?: boolean; // Loop through array of texts
  pauseDuration?: number; // Pause between loops (ms)
}

/**
 * Typewriter effect component with optional blinking cursor
 * Respects reduced motion preferences
 */
const TypewriterText: React.FC<TypewriterTextProps> = ({
  text,
  speed = 50,
  delay = 0,
  showCursor = true,
  cursorChar = '|',
  onComplete,
  loop = false,
  pauseDuration = 2000,
  ...typographyProps
}) => {
  const texts = Array.isArray(text) ? text : [text];
  const [currentTextIndex, setCurrentTextIndex] = useState(0);
  const [displayText, setDisplayText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [showCursorBlink, setShowCursorBlink] = useState(true);
  const prefersReducedMotion = useReducedMotion();

  useEffect(() => {
    // If user prefers reduced motion, show full text immediately
    if (prefersReducedMotion) {
      setDisplayText(texts[currentTextIndex]);
      setShowCursorBlink(false);
      if (onComplete) onComplete();
      return;
    }

    let timeout: NodeJS.Timeout;
    let charIndex = 0;
    const currentText = texts[currentTextIndex];

    // Initial delay before starting
    const startTyping = () => {
      setIsTyping(true);

      const typeNextChar = () => {
        if (charIndex < currentText.length) {
          setDisplayText(currentText.substring(0, charIndex + 1));
          charIndex++;
          timeout = setTimeout(typeNextChar, 1000 / speed);
        } else {
          setIsTyping(false);
          if (onComplete) onComplete();

          // Handle looping
          if (loop && texts.length > 1) {
            timeout = setTimeout(() => {
              setCurrentTextIndex((prev) => (prev + 1) % texts.length);
              setDisplayText('');
            }, pauseDuration);
          }
        }
      };

      timeout = setTimeout(typeNextChar, delay);
    };

    startTyping();

    return () => {
      if (timeout) clearTimeout(timeout);
    };
  }, [
    texts,
    currentTextIndex,
    speed,
    delay,
    onComplete,
    loop,
    pauseDuration,
    prefersReducedMotion,
  ]);

  // Cursor blink animation
  useEffect(() => {
    if (!showCursor || prefersReducedMotion) return;

    const interval = setInterval(() => {
      setShowCursorBlink((prev) => !prev);
    }, 530);

    return () => clearInterval(interval);
  }, [showCursor, prefersReducedMotion]);

  return (
    <Typography {...typographyProps} component="div">
      {displayText}
      {showCursor && (isTyping || loop) && (
        <motion.span
          animate={{ opacity: showCursorBlink ? 1 : 0 }}
          transition={{ duration: 0 }}
          style={{
            display: 'inline-block',
            marginLeft: '2px',
            fontWeight: 'normal',
          }}
        >
          {cursorChar}
        </motion.span>
      )}
    </Typography>
  );
};

export default TypewriterText;
