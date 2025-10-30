import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  Typography,
  Button,
  IconButton,
  Fade,
  Backdrop,
  Stepper,
  Step,
  StepLabel,
  useTheme,
  alpha,
} from '@mui/material';
import {
  Close,
  NavigateNext,
  NavigateBefore,
  School,
  CheckCircle,
  Lightbulb,
} from '@mui/icons-material';
import { keyframes } from '@mui/system';

const bounce = keyframes`
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
`;

const glow = keyframes`
  0% {
    box-shadow: 0 0 5px rgba(33, 150, 243, 0.5);
  }
  50% {
    box-shadow: 0 0 20px rgba(33, 150, 243, 0.8), 0 0 30px rgba(33, 150, 243, 0.6);
  }
  100% {
    box-shadow: 0 0 5px rgba(33, 150, 243, 0.5);
  }
`;

interface TourStep {
  target: string;
  title: string;
  content: string;
  position: 'top' | 'bottom' | 'left' | 'right';
  tips?: string[];
}

interface OnboardingTourProps {
  steps: TourStep[];
  onComplete?: () => void;
  onSkip?: () => void;
}

const OnboardingTour: React.FC<OnboardingTourProps> = ({ steps, onComplete, onSkip }) => {
  const theme = useTheme();
  const [currentStep, setCurrentStep] = useState(0);
  const [isOpen, setIsOpen] = useState(false);
  const [targetElement, setTargetElement] = useState<HTMLElement | null>(null);
  const [tooltipPosition, setTooltipPosition] = useState({ top: 0, left: 0 });

  useEffect(() => {
    const hasSeenTour = localStorage.getItem('marketingiq-tour-completed');
    if (!hasSeenTour) {
      setIsOpen(true);
    }
  }, []);

  useEffect(() => {
    if (isOpen && steps[currentStep]) {
      const element = document.querySelector(steps[currentStep].target) as HTMLElement;
      if (element) {
        setTargetElement(element);
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });

        // Add highlight effect
        element.style.position = 'relative';
        element.style.zIndex = '1301';
        element.style.animation = `${glow} 2s infinite`;

        // Calculate tooltip position
        const rect = element.getBoundingClientRect();
        const position = steps[currentStep].position;

        let top = 0, left = 0;
        switch (position) {
          case 'bottom':
            top = rect.bottom + 20;
            left = rect.left + rect.width / 2 - 200;
            break;
          case 'top':
            top = rect.top - 220;
            left = rect.left + rect.width / 2 - 200;
            break;
          case 'left':
            top = rect.top + rect.height / 2 - 100;
            left = rect.left - 420;
            break;
          case 'right':
            top = rect.top + rect.height / 2 - 100;
            left = rect.right + 20;
            break;
        }

        setTooltipPosition({ top, left: Math.max(20, left) });
      }
    }

    return () => {
      if (targetElement) {
        targetElement.style.animation = '';
        targetElement.style.zIndex = '';
      }
    };
  }, [currentStep, isOpen, steps]);

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = () => {
    localStorage.setItem('marketingiq-tour-completed', 'true');
    setIsOpen(false);
    onComplete?.();
  };

  const handleSkip = () => {
    localStorage.setItem('marketingiq-tour-completed', 'true');
    setIsOpen(false);
    onSkip?.();
  };

  if (!isOpen || !steps[currentStep]) return null;

  const currentStepData = steps[currentStep];

  return (
    <>
      <Backdrop
        open={isOpen}
        sx={{
          zIndex: 1300,
          bgcolor: alpha(theme.palette.common.black, 0.7),
          backdropFilter: 'blur(3px)',
        }}
      />

      <Fade in={isOpen}>
        <Card
          sx={{
            position: 'fixed',
            top: tooltipPosition.top,
            left: tooltipPosition.left,
            zIndex: 1302,
            width: 400,
            p: 3,
            background: `linear-gradient(135deg, ${theme.palette.background.paper} 0%, ${alpha(
              theme.palette.primary.main,
              0.05
            )} 100%)`,
            border: `2px solid ${theme.palette.primary.main}`,
            borderRadius: 2,
            boxShadow: `0 10px 40px ${alpha(theme.palette.primary.main, 0.3)}`,
            animation: `${bounce} 2s infinite`,
          }}
        >
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <School sx={{ color: theme.palette.primary.main }} />
              <Typography variant="caption" color="primary">
                Step {currentStep + 1} of {steps.length}
              </Typography>
            </Box>
            <IconButton size="small" onClick={handleSkip}>
              <Close />
            </IconButton>
          </Box>

          <Typography variant="h6" sx={{ mb: 1, fontWeight: 600, color: theme.palette.primary.main }}>
            {currentStepData.title}
          </Typography>

          <Typography variant="body2" sx={{ mb: 2, color: theme.palette.text.secondary }}>
            {currentStepData.content}
          </Typography>

          {currentStepData.tips && currentStepData.tips.length > 0 && (
            <Box
              sx={{
                p: 2,
                mb: 2,
                borderRadius: 1,
                bgcolor: alpha(theme.palette.info.main, 0.1),
                border: `1px solid ${alpha(theme.palette.info.main, 0.3)}`,
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
                <Lightbulb sx={{ fontSize: 16, color: theme.palette.info.main }} />
                <Typography variant="caption" sx={{ fontWeight: 600, color: theme.palette.info.main }}>
                  Pro Tips
                </Typography>
              </Box>
              {currentStepData.tips.map((tip, index) => (
                <Typography key={index} variant="caption" sx={{ display: 'block', mb: 0.5 }}>
                  • {tip}
                </Typography>
              ))}
            </Box>
          )}

          <Stepper activeStep={currentStep} sx={{ mb: 2 }}>
            {steps.map((_, index) => (
              <Step key={index} sx={{ '& .MuiStepLabel-root': { display: 'none' } }}>
                <StepLabel />
              </Step>
            ))}
          </Stepper>

          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Button
              startIcon={<NavigateBefore />}
              onClick={handlePrevious}
              disabled={currentStep === 0}
              variant="outlined"
            >
              Previous
            </Button>

            {currentStep === steps.length - 1 ? (
              <Button
                endIcon={<CheckCircle />}
                onClick={handleComplete}
                variant="contained"
                sx={{
                  background: `linear-gradient(45deg, ${theme.palette.primary.main} 30%, ${theme.palette.secondary.main} 90%)`,
                }}
              >
                Complete Tour
              </Button>
            ) : (
              <Button
                endIcon={<NavigateNext />}
                onClick={handleNext}
                variant="contained"
                sx={{
                  background: `linear-gradient(45deg, ${theme.palette.primary.main} 30%, ${theme.palette.secondary.main} 90%)`,
                }}
              >
                Next
              </Button>
            )}
          </Box>
        </Card>
      </Fade>
    </>
  );
};

export default OnboardingTour;