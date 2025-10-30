// Landing Page - Enhanced Scroll Story Experience
import React, { useRef } from 'react';
import { Box, Button, Container, Typography, Grid, Paper } from '@mui/material';
import { motion, useScroll, useTransform } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  TrendingUp as TrendingUpIcon,
  Speed as SpeedIcon,
  Psychology as PsychologyIcon,
  Timeline as TimelineIcon,
  Warning as WarningIcon,
  AttachMoney as AttachMoneyIcon,
} from '@mui/icons-material';

// Import animation utilities
import {
  fadeInUp,
  blurInScale,
  cardAnimation,
  staggerContainer,
  viewportConfig,
  iconPulse,
} from '../../utils/animations';

// Import effect components
import {
  ParticleBackground,
  ParallaxLayer,
  TypewriterText,
  MagneticButton,
  TiltCard,
} from './effects';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const heroRef = useRef<HTMLDivElement>(null);

  const { scrollYProgress } = useScroll();
  const heroOpacity = useTransform(scrollYProgress, [0, 0.1], [1, 0.6]);

  // Parallax effects for hero background
  const { scrollYProgress: heroScrollProgress } = useScroll({
    target: heroRef,
    offset: ['start start', 'end start'],
  });
  const heroY = useTransform(heroScrollProgress, [0, 1], [0, 200]);

  return (
    <Box sx={{ bgcolor: '#F8F9FA', minHeight: '100vh' }}>
      {/* Hero Section */}
      <motion.div style={{ opacity: heroOpacity }}>
        <Box
          ref={heroRef}
          sx={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #1E88E5 0%, #42A5F5 100%)',
            color: 'white',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          {/* Particle Background */}
          <ParticleBackground
            particleCount={60}
            particleColor="rgba(255, 255, 255, 0.6)"
            connectionColor="rgba(255, 255, 255, 0.2)"
            connectionDistance={150}
            speed={0.3}
          />

          {/* Parallax Background Layers */}
          <motion.div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              y: heroY,
              opacity: 0.1,
            }}
          >
            <Box
              sx={{
                position: 'absolute',
                top: '10%',
                left: '10%',
                width: 300,
                height: 300,
                borderRadius: '50%',
                background: 'radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%)',
                filter: 'blur(40px)',
              }}
            />
            <Box
              sx={{
                position: 'absolute',
                bottom: '10%',
                right: '10%',
                width: 400,
                height: 400,
                borderRadius: '50%',
                background: 'radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%)',
                filter: 'blur(60px)',
              }}
            />
          </motion.div>

          <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
            {/* Title with Typewriter Effect */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.8 }}
            >
              <TypewriterText
                text="Marketing Intelligence Platform"
                speed={60}
                delay={500}
                showCursor={false}
                variant="h1"
                align="center"
                sx={{
                  fontWeight: 800,
                  mb: 3,
                  fontSize: { xs: '2.5rem', md: '4rem' },
                }}
              />
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.5, duration: 0.8 }}
            >
              <Typography
                variant="h4"
                align="center"
                sx={{
                  fontWeight: 400,
                  mb: 2,
                  opacity: 0.95,
                  fontSize: { xs: '1.5rem', md: '2rem' },
                }}
              >
                One Dashboard. Three Platforms. Infinite Insights.
              </Typography>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.8, duration: 0.8 }}
            >
              <Typography
                variant="h6"
                align="center"
                sx={{
                  fontWeight: 300,
                  mb: 5,
                  opacity: 0.9,
                  maxWidth: 800,
                  mx: 'auto',
                }}
              >
                Real-time analytics across Google Ads, Meta Ads, and Google Analytics — powered by AI.
              </Typography>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 2.1, duration: 0.6 }}
            >
              <Box display="flex" justifyContent="center" gap={2} flexWrap="wrap">
                <Button
                  variant="contained"
                  size="large"
                  onClick={() => navigate('/dashboard/unified')}
                  sx={{
                    bgcolor: 'white',
                    color: 'primary.main',
                    px: 4,
                    py: 1.5,
                    fontSize: '1.1rem',
                    boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
                    '&:hover': {
                      bgcolor: 'grey.100',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 6px 30px rgba(0,0,0,0.15)',
                    },
                    transition: 'all 0.3s ease',
                  }}
                >
                  Get Started
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  onClick={() => navigate('/dashboard/unified')}
                  sx={{
                    borderColor: 'white',
                    color: 'white',
                    px: 4,
                    py: 1.5,
                    fontSize: '1.1rem',
                    '&:hover': {
                      borderColor: 'white',
                      bgcolor: 'rgba(255,255,255,0.1)',
                      transform: 'translateY(-2px)',
                    },
                    transition: 'all 0.3s ease',
                  }}
                >
                  View Demo
                </Button>
              </Box>
            </motion.div>
          </Container>
        </Box>
      </motion.div>

      {/* Platform Integration Section */}
      <ParallaxLayer speed={0.3}>
        <Container maxWidth="lg" sx={{ py: 12 }}>
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={viewportConfig}
            variants={fadeInUp}
          >
            <Typography
              variant="h3"
              align="center"
              gutterBottom
              sx={{ fontWeight: 700, mb: 2 }}
            >
              Unified Cross-Platform Analytics
            </Typography>
            <Typography
              variant="body1"
              align="center"
              color="text.secondary"
              sx={{ mb: 6, maxWidth: 700, mx: 'auto' }}
            >
              Seamlessly integrate data from multiple marketing platforms for comprehensive insights
            </Typography>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={viewportConfig}
            variants={staggerContainer}
          >
            <Grid container spacing={4} justifyContent="center">
              {[
                {
                  title: 'Google Ads',
                  desc: 'Search, Display, Shopping campaigns unified',
                  color: '#4285F4',
                  icon: '🎯',
                },
                {
                  title: 'Meta Ads',
                  desc: 'Facebook & Instagram advertising insights',
                  color: '#0084FF',
                  icon: '📱',
                },
                {
                  title: 'Google Analytics',
                  desc: 'Website traffic and conversion tracking',
                  color: '#E37400',
                  icon: '📊',
                },
              ].map((platform, i) => (
                <Grid item xs={12} md={4} key={i}>
                  <motion.div variants={blurInScale}>
                    <TiltCard
                      tiltIntensity={0.4}
                      glareEffect
                      maxTilt={10}
                      elevation={3}
                      sx={{
                        height: '100%',
                        background: 'linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)',
                        border: `2px solid ${platform.color}20`,
                        transition: 'border-color 0.3s ease',
                        '&:hover': {
                          borderColor: `${platform.color}60`,
                        },
                      }}
                    >
                      <Box sx={{ p: 4, textAlign: 'center' }}>
                        <motion.div
                          initial="hidden"
                          whileInView="visible"
                          variants={iconPulse}
                          viewport={{ once: true }}
                        >
                          <Box
                            sx={{
                              fontSize: '4rem',
                              mb: 2,
                              display: 'flex',
                              justifyContent: 'center',
                            }}
                          >
                            {platform.icon}
                          </Box>
                        </motion.div>
                        <Typography
                          variant="h5"
                          gutterBottom
                          sx={{
                            fontWeight: 600,
                            color: platform.color,
                          }}
                        >
                          {platform.title}
                        </Typography>
                        <Typography variant="body1" color="text.secondary">
                          {platform.desc}
                        </Typography>
                      </Box>
                    </TiltCard>
                  </motion.div>
                </Grid>
              ))}
            </Grid>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={viewportConfig}
            variants={fadeInUp}
            transition={{ delay: 0.5 }}
          >
            <Typography
              variant="h6"
              align="center"
              sx={{
                mt: 6,
                color: 'text.secondary',
                fontWeight: 400,
              }}
            >
              All your marketing data in one place.
            </Typography>
          </motion.div>
        </Container>
      </ParallaxLayer>

      {/* Features Section */}
      <Box sx={{ bgcolor: 'white', py: 12 }}>
        <Container maxWidth="lg">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={viewportConfig}
            variants={fadeInUp}
          >
            <Typography
              variant="h3"
              align="center"
              gutterBottom
              sx={{ fontWeight: 700, mb: 2 }}
            >
              Platform Capabilities
            </Typography>
            <Typography
              variant="body1"
              align="center"
              color="text.secondary"
              sx={{ mb: 6, maxWidth: 700, mx: 'auto' }}
            >
              Powered by advanced AI and real-time data processing
            </Typography>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={viewportConfig}
            variants={staggerContainer}
          >
            <Grid container spacing={3}>
              {[
                {
                  title: 'Real-Time Monitoring',
                  icon: SpeedIcon,
                  color: '#1E88E5',
                  direction: 'left' as const,
                },
                {
                  title: 'AI-Powered Insights',
                  icon: PsychologyIcon,
                  color: '#7B1FA2',
                  direction: 'up' as const,
                },
                {
                  title: 'Multi-Agent System',
                  icon: TrendingUpIcon,
                  color: '#388E3C',
                  direction: 'right' as const,
                },
                {
                  title: 'Forecasting & Predictions',
                  icon: TimelineIcon,
                  color: '#F57C00',
                  direction: 'left' as const,
                },
                {
                  title: 'Anomaly Detection',
                  icon: WarningIcon,
                  color: '#D32F2F',
                  direction: 'down' as const,
                },
                {
                  title: 'Budget Optimization',
                  icon: AttachMoneyIcon,
                  color: '#00897B',
                  direction: 'right' as const,
                },
              ].map((feature, i) => {
                const IconComponent = feature.icon;
                return (
                  <Grid item xs={12} sm={6} md={4} key={i}>
                    <motion.div
                      variants={cardAnimation(feature.direction, i)}
                      whileHover={{
                        scale: 1.05,
                        y: -8,
                        transition: { duration: 0.2 },
                      }}
                    >
                      <Paper
                        elevation={2}
                        sx={{
                          p: 4,
                          textAlign: 'center',
                          height: '100%',
                          borderTop: `4px solid ${feature.color}`,
                          transition: 'all 0.3s ease',
                          cursor: 'pointer',
                          '&:hover': {
                            boxShadow: '0 8px 24px rgba(0,0,0,0.12)',
                          },
                        }}
                      >
                        <motion.div
                          initial={{ scale: 1, rotate: 0 }}
                          whileHover={{
                            scale: 1.2,
                            rotate: 360,
                            transition: { duration: 0.6 },
                          }}
                        >
                          <IconComponent
                            sx={{
                              fontSize: 48,
                              color: feature.color,
                              mb: 2,
                            }}
                          />
                        </motion.div>
                        <Typography
                          variant="h6"
                          sx={{
                            fontWeight: 600,
                            color: 'text.primary',
                          }}
                        >
                          {feature.title}
                        </Typography>
                      </Paper>
                    </motion.div>
                  </Grid>
                );
              })}
            </Grid>
          </motion.div>
        </Container>
      </Box>

      {/* CTA Section */}
      <ParallaxLayer speed={-0.2}>
        <Box
          sx={{
            py: 12,
            background: 'linear-gradient(135deg, #1E88E5 0%, #42A5F5 100%)',
            color: 'white',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          {/* Background decoration */}
          <Box
            sx={{
              position: 'absolute',
              top: '-50%',
              right: '-10%',
              width: 400,
              height: 400,
              borderRadius: '50%',
              background: 'radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%)',
              filter: 'blur(60px)',
            }}
          />
          <Box
            sx={{
              position: 'absolute',
              bottom: '-50%',
              left: '-10%',
              width: 500,
              height: 500,
              borderRadius: '50%',
              background: 'radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%)',
              filter: 'blur(80px)',
            }}
          />

          <Container maxWidth="md" sx={{ position: 'relative', zIndex: 1 }}>
            <motion.div
              initial="hidden"
              whileInView="visible"
              viewport={viewportConfig}
              variants={fadeInUp}
            >
              <Typography
                variant="h3"
                align="center"
                gutterBottom
                sx={{
                  fontWeight: 700,
                  mb: 2,
                  fontSize: { xs: '2rem', md: '3rem' },
                }}
              >
                Ready to optimize your marketing?
              </Typography>
              <Typography
                variant="h6"
                align="center"
                sx={{
                  fontWeight: 300,
                  opacity: 0.9,
                  mb: 4,
                }}
              >
                Join the future of intelligent marketing analytics
              </Typography>
            </motion.div>

            <Box display="flex" justifyContent="center" mt={4}>
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={viewportConfig}
                transition={{ delay: 0.3, duration: 0.5 }}
              >
                <MagneticButton
                  variant="contained"
                  size="large"
                  onClick={() => navigate('/dashboard/unified')}
                  magneticStrength={0.4}
                  magneticRange={150}
                  glowEffect
                  sx={{
                    bgcolor: 'white',
                    color: 'primary.main',
                    px: 6,
                    py: 2,
                    fontSize: '1.2rem',
                    fontWeight: 600,
                    boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
                    '&:hover': {
                      bgcolor: 'grey.100',
                      boxShadow: '0 12px 48px rgba(0,0,0,0.3)',
                    },
                    transition: 'all 0.3s ease',
                  }}
                >
                  Get Started Now
                </MagneticButton>
              </motion.div>
            </Box>

            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={viewportConfig}
              transition={{ delay: 0.6 }}
            >
              <Typography
                variant="body2"
                align="center"
                sx={{
                  mt: 3,
                  opacity: 0.8,
                }}
              >
                No credit card required • Start free trial
              </Typography>
            </motion.div>
          </Container>
        </Box>
      </ParallaxLayer>
    </Box>
  );
};
