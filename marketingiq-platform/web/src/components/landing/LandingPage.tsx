// Landing Page - Complete Single Page Application
import React, { useRef, useState } from 'react';
import {
  Box,
  Button,
  Container,
  Typography,
  Grid,
  Paper,
  AppBar,
  Toolbar,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemText,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Card,
  CardContent,
  Divider,
  Avatar,
  Stack,
  Link as MuiLink,
} from '@mui/material';
import { motion, useScroll, useTransform } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  TrendingUp as TrendingUpIcon,
  Speed as SpeedIcon,
  Psychology as PsychologyIcon,
  Timeline as TimelineIcon,
  Warning as WarningIcon,
  AttachMoney as AttachMoneyIcon,
  Menu as MenuIcon,
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
  Star as StarIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  LocationOn as LocationOnIcon,
  LinkedIn as LinkedInIcon,
  Twitter as TwitterIcon,
  GitHub as GitHubIcon,
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
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const { scrollYProgress } = useScroll();
  const heroOpacity = useTransform(scrollYProgress, [0, 0.1], [1, 0.6]);

  // Parallax effects for hero background
  const { scrollYProgress: heroScrollProgress } = useScroll({
    target: heroRef,
    offset: ['start start', 'end start'],
  });
  const heroY = useTransform(heroScrollProgress, [0, 1], [0, 200]);

  // Navigation menu items
  const navItems = [
    { label: 'Home', href: '#hero' },
    { label: 'Features', href: '#features' },
    { label: 'Platforms', href: '#platforms' },
    { label: 'How It Works', href: '#how-it-works' },
    { label: 'Pricing', href: '#pricing' },
    { label: 'FAQ', href: '#faq' },
    { label: 'Contact', href: '#contact' },
  ];

  // Smooth scroll to section
  const scrollToSection = (href: string) => {
    const element = document.querySelector(href);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      setMobileMenuOpen(false);
    }
  };

  return (
    <Box sx={{ bgcolor: '#F8F9FA', minHeight: '100vh', position: 'relative' }}>
      {/* Sticky Navigation Header */}
      <AppBar
        position="fixed"
        sx={{
          bgcolor: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
          color: 'text.primary',
        }}
      >
        <Container maxWidth="lg">
          <Toolbar sx={{ justifyContent: 'space-between' }}>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 700,
                color: 'primary.main',
                cursor: 'pointer',
                minWidth: '150px',
                whiteSpace: 'nowrap',
                overflow: 'visible'
              }}
              onClick={() => scrollToSection('#hero')}
            >
              Marketing IQ
            </Typography>

            {/* Desktop Menu */}
            <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 3 }}>
              {navItems.map((item) => (
                <Button
                  key={item.label}
                  onClick={() => scrollToSection(item.href)}
                  sx={{
                    color: 'text.primary',
                    fontWeight: 500,
                    '&:hover': { color: 'primary.main' },
                  }}
                >
                  {item.label}
                </Button>
              ))}
              <Button
                variant="contained"
                onClick={() => navigate('/dashboard/unified')}
                sx={{
                  ml: 2,
                  fontWeight: 600,
                  px: 3,
                  '&:hover': {
                    transform: 'translateY(-1px)',
                    boxShadow: 3,
                  },
                  transition: 'all 0.2s ease',
                }}
              >
                Start Free Trial
              </Button>
            </Box>

            {/* Mobile Menu Button */}
            <IconButton
              sx={{ display: { xs: 'block', md: 'none' } }}
              onClick={() => setMobileMenuOpen(true)}
            >
              <MenuIcon />
            </IconButton>
          </Toolbar>
        </Container>
      </AppBar>

      {/* Mobile Drawer Menu */}
      <Drawer
        anchor="right"
        open={mobileMenuOpen}
        onClose={() => setMobileMenuOpen(false)}
      >
        <Box sx={{ width: 250, pt: 2 }}>
          <List>
            {navItems.map((item) => (
              <ListItem key={item.label} onClick={() => scrollToSection(item.href)}>
                <ListItemText primary={item.label} />
              </ListItem>
            ))}
            <ListItem>
              <Button
                variant="contained"
                fullWidth
                onClick={() => navigate('/dashboard/unified')}
                sx={{ fontWeight: 600 }}
              >
                Start Free Trial
              </Button>
            </ListItem>
          </List>
        </Box>
      </Drawer>
      {/* Hero Section */}
      <motion.div style={{ opacity: heroOpacity, position: 'relative' }} id="hero">
        <Box
          ref={heroRef}
          sx={{
            mt: 8,
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: `
              linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 249, 250, 0.92) 100%),
              url('https://images.unsplash.com/photo-1557804506-669a67965ba0?q=80&w=1600&auto=format&fit=crop')
            `,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            backgroundAttachment: 'fixed',
            color: 'text.primary',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          {/* Particle Background */}
          <ParticleBackground
            particleCount={60}
            particleColor="rgba(30, 136, 229, 0.4)"
            connectionColor="rgba(30, 136, 229, 0.15)"
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
              opacity: 0.3,
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
                background: 'radial-gradient(circle, rgba(30, 136, 229, 0.2) 0%, transparent 70%)',
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
                background: 'radial-gradient(circle, rgba(123, 31, 162, 0.15) 0%, transparent 70%)',
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
              <Typography
                variant="h1"
                align="center"
                sx={{
                  fontWeight: 800,
                  mb: 3,
                  fontSize: { xs: '2.5rem', md: '4.5rem' },
                  background: 'linear-gradient(135deg, #1E88E5 0%, #7B1FA2 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                }}
              >
                Marketing Intelligence
              </Typography>
              <Typography
                variant="h2"
                align="center"
                sx={{
                  fontWeight: 700,
                  mb: 4,
                  fontSize: { xs: '2rem', md: '3.5rem' },
                  color: 'text.primary',
                }}
              >
                Powered by AI
              </Typography>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8, duration: 0.8 }}
            >
              <Typography
                variant="h4"
                align="center"
                sx={{
                  fontWeight: 500,
                  mb: 2,
                  opacity: 0.95,
                  fontSize: { xs: '1.5rem', md: '2.2rem' },
                }}
              >
                Unify. Analyze. Optimize.
              </Typography>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.1, duration: 0.8 }}
            >
              <Typography
                variant="h6"
                align="center"
                sx={{
                  fontWeight: 300,
                  mb: 5,
                  opacity: 0.85,
                  maxWidth: 900,
                  mx: 'auto',
                  lineHeight: 1.6,
                }}
              >
                Connect Google Ads, Meta Ads, and Google Analytics in one intelligent dashboard.
                Get real-time insights, predictive analytics, and AI-powered recommendations to maximize your ROAS.
              </Typography>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 1.4, duration: 0.6 }}
            >
              <Box display="flex" justifyContent="center" gap={2} flexWrap="wrap">
                <Button
                  variant="contained"
                  size="large"
                  onClick={() => navigate('/dashboard/unified')}
                  sx={{
                    bgcolor: 'primary.main',
                    color: 'white',
                    px: 5,
                    py: 2,
                    fontSize: '1.2rem',
                    fontWeight: 600,
                    boxShadow: '0 4px 20px rgba(30, 136, 229, 0.3)',
                    '&:hover': {
                      bgcolor: 'primary.dark',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 6px 30px rgba(30, 136, 229, 0.4)',
                    },
                    transition: 'all 0.3s ease',
                  }}
                >
                  Start Free Trial
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  onClick={() => navigate('/dashboard/unified')}
                  sx={{
                    borderColor: 'primary.main',
                    borderWidth: 2,
                    color: 'primary.main',
                    px: 5,
                    py: 2,
                    fontSize: '1.2rem',
                    fontWeight: 600,
                    '&:hover': {
                      borderColor: 'primary.dark',
                      borderWidth: 2,
                      bgcolor: 'rgba(30, 136, 229, 0.05)',
                      transform: 'translateY(-2px)',
                    },
                    transition: 'all 0.3s ease',
                  }}
                >
                  View Live Demo
                </Button>
              </Box>
            </motion.div>

            {/* Quick benefits */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.8, duration: 0.6 }}
            >
              <Stack
                direction={{ xs: 'column', sm: 'row' }}
                spacing={4}
                justifyContent="center"
                alignItems="center"
                sx={{ mt: 6 }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CheckCircleIcon sx={{ color: 'success.main', fontSize: 24 }} />
                  <Typography variant="body1" sx={{ fontWeight: 500 }}>
                    14-day free trial
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CheckCircleIcon sx={{ color: 'success.main', fontSize: 24 }} />
                  <Typography variant="body1" sx={{ fontWeight: 500 }}>
                    No credit card required
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CheckCircleIcon sx={{ color: 'success.main', fontSize: 24 }} />
                  <Typography variant="body1" sx={{ fontWeight: 500 }}>
                    Cancel anytime
                  </Typography>
                </Box>
              </Stack>
            </motion.div>
          </Container>
        </Box>
      </motion.div>

      {/* Platform Integration Section */}
      <ParallaxLayer speed={0.3}>
        <Box
          id="platforms"
          sx={{
            background: `
              linear-gradient(to bottom, rgba(248, 249, 250, 0.97), rgba(255, 255, 255, 0.95)),
              url('https://images.unsplash.com/photo-1639762681485-074b7f938ba0?q=80&w=1600&auto=format&fit=crop')
            `,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            backgroundAttachment: 'fixed',
            py: 12,
          }}
        >
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
                        background: `
                          linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 249, 250, 0.9) 100%),
                          url('https://images.unsplash.com/photo-1639762681485-074b7f938ba0?q=80&w=800&auto=format&fit=crop')
                        `,
                        backgroundSize: 'cover',
                        backgroundPosition: 'center',
                        backdropFilter: 'blur(10px)',
                        border: `2px solid ${platform.color}20`,
                        transition: 'all 0.3s ease',
                        '&:hover': {
                          borderColor: `${platform.color}60`,
                          boxShadow: `0 8px 32px ${platform.color}30`,
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
        </Box>
      </ParallaxLayer>

      {/* Features Section */}
      <Box
        id="features"
        sx={{
          background: `
            linear-gradient(to bottom, rgba(255, 255, 255, 0.98), rgba(255, 255, 255, 0.96)),
            url('https://images.unsplash.com/photo-1677442136019-21780ecad995?q=80&w=1600&auto=format&fit=crop')
          `,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          py: 12,
        }}
      >
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

      {/* How It Works Section */}
      <Box id="how-it-works" sx={{ py: 12, bgcolor: '#F8F9FA' }}>
        <Container maxWidth="lg">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={viewportConfig}
            variants={fadeInUp}
          >
            <Typography variant="h3" align="center" gutterBottom sx={{ fontWeight: 700, mb: 2 }}>
              How It Works
            </Typography>
            <Typography variant="body1" align="center" color="text.secondary" sx={{ mb: 8, maxWidth: 700, mx: 'auto' }}>
              Get started in minutes with our simple 3-step process
            </Typography>
          </motion.div>

          <Grid container spacing={6} alignItems="center">
            {[
              {
                step: '1',
                title: 'Connect Your Platforms',
                desc: 'Integrate Google Ads, Meta Ads, and Google Analytics with one-click authentication',
                color: '#1E88E5',
              },
              {
                step: '2',
                title: 'AI Analyzes Your Data',
                desc: 'Our multi-agent system processes your campaigns and generates intelligent insights',
                color: '#7B1FA2',
              },
              {
                step: '3',
                title: 'Optimize & Scale',
                desc: 'Implement AI-powered recommendations and watch your ROAS improve',
                color: '#388E3C',
              },
            ].map((item, i) => (
              <Grid item xs={12} md={4} key={i}>
                <motion.div
                  initial={{ opacity: 0, x: i % 2 === 0 ? -50 : 50 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={viewportConfig}
                  transition={{ delay: i * 0.2 }}
                >
                  <Card
                    sx={{
                      p: 4,
                      textAlign: 'center',
                      height: '100%',
                      border: `2px solid ${item.color}20`,
                      '&:hover': {
                        borderColor: item.color,
                        transform: 'translateY(-8px)',
                      },
                      transition: 'all 0.3s ease',
                    }}
                  >
                    <Box
                      sx={{
                        width: 60,
                        height: 60,
                        borderRadius: '50%',
                        bgcolor: item.color,
                        color: 'white',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '2rem',
                        fontWeight: 700,
                        mx: 'auto',
                        mb: 3,
                      }}
                    >
                      {item.step}
                    </Box>
                    <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                      {item.title}
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                      {item.desc}
                    </Typography>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* Pricing Section */}
      <Box id="pricing" sx={{ py: 12, bgcolor: 'white' }}>
        <Container maxWidth="lg">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={viewportConfig}
            variants={fadeInUp}
          >
            <Typography variant="h3" align="center" gutterBottom sx={{ fontWeight: 700, mb: 2 }}>
              Simple, Transparent Pricing
            </Typography>
            <Typography variant="body1" align="center" color="text.secondary" sx={{ mb: 8, maxWidth: 700, mx: 'auto' }}>
              Choose the plan that fits your business needs
            </Typography>
          </motion.div>

          <Grid container spacing={4} justifyContent="center">
            {[
              {
                name: 'Starter',
                price: '$99',
                period: '/month',
                features: [
                  'Up to 3 campaigns',
                  'Google Ads integration',
                  'Basic AI insights',
                  'Email support',
                  '7-day data retention',
                ],
                color: '#1E88E5',
                popular: false,
              },
              {
                name: 'Professional',
                price: '$299',
                period: '/month',
                features: [
                  'Unlimited campaigns',
                  'All platform integrations',
                  'Advanced AI insights',
                  'Priority support',
                  '90-day data retention',
                  'Custom reports',
                  'API access',
                ],
                color: '#7B1FA2',
                popular: true,
              },
              {
                name: 'Enterprise',
                price: 'Custom',
                period: '',
                features: [
                  'Everything in Professional',
                  'Dedicated account manager',
                  'Custom integrations',
                  'Unlimited data retention',
                  'White-label option',
                  'SLA guarantee',
                ],
                color: '#388E3C',
                popular: false,
              },
            ].map((plan, i) => (
              <Grid item xs={12} md={4} key={i}>
                <motion.div
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={viewportConfig}
                  transition={{ delay: i * 0.15 }}
                >
                  <Card
                    sx={{
                      p: 4,
                      height: '100%',
                      position: 'relative',
                      border: plan.popular ? `3px solid ${plan.color}` : '1px solid #E0E0E0',
                      transform: plan.popular ? 'scale(1.05)' : 'scale(1)',
                      '&:hover': {
                        transform: plan.popular ? 'scale(1.08)' : 'scale(1.03)',
                        boxShadow: '0 8px 24px rgba(0,0,0,0.12)',
                      },
                      transition: 'all 0.3s ease',
                    }}
                  >
                    {plan.popular && (
                      <Box
                        sx={{
                          position: 'absolute',
                          top: -15,
                          left: '50%',
                          transform: 'translateX(-50%)',
                          bgcolor: plan.color,
                          color: 'white',
                          px: 3,
                          py: 0.5,
                          borderRadius: 2,
                          fontWeight: 600,
                          fontSize: '0.875rem',
                        }}
                      >
                        MOST POPULAR
                      </Box>
                    )}
                    <Typography
                      variant="h5"
                      align="center"
                      sx={{ fontWeight: 600, mb: 2, color: plan.color }}
                    >
                      {plan.name}
                    </Typography>
                    <Box sx={{ textAlign: 'center', mb: 3 }}>
                      <Typography variant="h2" sx={{ fontWeight: 700, color: plan.color }}>
                        {plan.price}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {plan.period}
                      </Typography>
                    </Box>
                    <Divider sx={{ mb: 3 }} />
                    <Stack spacing={2} sx={{ mb: 4 }}>
                      {plan.features.map((feature, idx) => (
                        <Box key={idx} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <CheckCircleIcon sx={{ color: plan.color, fontSize: 20 }} />
                          <Typography variant="body2">{feature}</Typography>
                        </Box>
                      ))}
                    </Stack>
                    <Button
                      variant={plan.popular ? 'contained' : 'outlined'}
                      fullWidth
                      size="large"
                      sx={{
                        bgcolor: plan.popular ? plan.color : 'transparent',
                        borderColor: plan.color,
                        color: plan.popular ? 'white' : plan.color,
                        '&:hover': {
                          bgcolor: plan.popular ? `${plan.color}dd` : `${plan.color}10`,
                          borderColor: plan.color,
                        },
                      }}
                      onClick={() => navigate('/dashboard/unified')}
                    >
                      {plan.price === 'Custom' ? 'Contact Sales' : 'Get Started'}
                    </Button>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* FAQ Section */}
      <Box id="faq" sx={{ py: 12, bgcolor: '#F8F9FA' }}>
        <Container maxWidth="md">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={viewportConfig}
            variants={fadeInUp}
          >
            <Typography variant="h3" align="center" gutterBottom sx={{ fontWeight: 700, mb: 2 }}>
              Frequently Asked Questions
            </Typography>
            <Typography variant="body1" align="center" color="text.secondary" sx={{ mb: 6 }}>
              Everything you need to know about Marketing IQ
            </Typography>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={viewportConfig}
            variants={staggerContainer}
          >
            {[
              {
                q: 'How long does it take to set up?',
                a: 'Most customers are up and running in less than 15 minutes. Our one-click integrations make connecting your platforms quick and easy.',
              },
              {
                q: 'Do I need technical expertise to use MarketingIQ?',
                a: 'No technical knowledge required! Our AI-powered insights are presented in plain language, and our intuitive dashboards are designed for marketers, not developers.',
              },
              {
                q: 'Can I cancel anytime?',
                a: 'Absolutely. All our plans are month-to-month with no long-term commitments. You can cancel anytime from your account settings.',
              },
              {
                q: 'What platforms do you integrate with?',
                a: 'Currently we integrate with Google Ads, Meta Ads (Facebook & Instagram), and Google Analytics 4. We\'re constantly adding new integrations based on customer feedback.',
              },
              {
                q: 'Is my data secure?',
                a: 'Security is our top priority. We use enterprise-grade encryption, SOC 2 compliance, and never share your data with third parties. All data is stored in secure, redundant data centers.',
              },
              {
                q: 'Do you offer a free trial?',
                a: 'Yes! We offer a 14-day free trial on all plans. No credit card required. You can explore all features and see real results before committing.',
              },
            ].map((faq, i) => (
              <motion.div key={i} variants={cardAnimation('up', i)}>
                <Accordion
                  sx={{
                    mb: 2,
                    '&:before': { display: 'none' },
                    boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                  }}
                >
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {faq.q}
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography color="text.secondary">{faq.a}</Typography>
                  </AccordionDetails>
                </Accordion>
              </motion.div>
            ))}
          </motion.div>
        </Container>
      </Box>

      {/* CTA Section */}
      <ParallaxLayer speed={-0.2}>
        <Box
          sx={{
            py: 12,
            background: `
              linear-gradient(135deg, rgba(15, 23, 42, 0.88) 0%, rgba(30, 41, 59, 0.82) 100%),
              url('https://images.unsplash.com/photo-1519389950473-47ba0277781c?q=80&w=1600&auto=format&fit=crop')
            `,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            backgroundAttachment: 'fixed',
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

      {/* Contact/Footer Section */}
      <Box id="contact" sx={{ bgcolor: '#1E293B', color: 'white', py: 8 }}>
        <Container maxWidth="lg">
          <Grid container spacing={6}>
            {/* Company Info */}
            <Grid item xs={12} md={4}>
              <Typography variant="h5" sx={{ fontWeight: 700, mb: 2 }}>
                Marketing IQ
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8, mb: 3 }}>
                Empower your marketing decisions with AI-powered intelligence. Unified analytics across Google Ads, Meta Ads, and Google Analytics - all in one powerful dashboard.
              </Typography>
              <Stack direction="row" spacing={2}>
                <IconButton sx={{ color: 'white', bgcolor: 'rgba(255,255,255,0.1)' }}>
                  <LinkedInIcon />
                </IconButton>
                <IconButton sx={{ color: 'white', bgcolor: 'rgba(255,255,255,0.1)' }}>
                  <TwitterIcon />
                </IconButton>
                <IconButton sx={{ color: 'white', bgcolor: 'rgba(255,255,255,0.1)' }}>
                  <GitHubIcon />
                </IconButton>
              </Stack>
            </Grid>

            {/* Quick Links */}
            <Grid item xs={12} sm={6} md={2}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                Product
              </Typography>
              <Stack spacing={1}>
                {['Features', 'Pricing', 'Integrations', 'API Docs'].map((link) => (
                  <MuiLink
                    key={link}
                    sx={{
                      color: 'rgba(255,255,255,0.7)',
                      textDecoration: 'none',
                      '&:hover': { color: 'white' },
                      cursor: 'pointer',
                    }}
                  >
                    {link}
                  </MuiLink>
                ))}
              </Stack>
            </Grid>

            <Grid item xs={12} sm={6} md={2}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                Company
              </Typography>
              <Stack spacing={1}>
                {['About Us', 'Careers', 'Blog', 'Press Kit'].map((link) => (
                  <MuiLink
                    key={link}
                    sx={{
                      color: 'rgba(255,255,255,0.7)',
                      textDecoration: 'none',
                      '&:hover': { color: 'white' },
                      cursor: 'pointer',
                    }}
                  >
                    {link}
                  </MuiLink>
                ))}
              </Stack>
            </Grid>

            <Grid item xs={12} sm={6} md={2}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                Support
              </Typography>
              <Stack spacing={1}>
                {['Help Center', 'Contact', 'Status', 'Terms'].map((link) => (
                  <MuiLink
                    key={link}
                    sx={{
                      color: 'rgba(255,255,255,0.7)',
                      textDecoration: 'none',
                      '&:hover': { color: 'white' },
                      cursor: 'pointer',
                    }}
                  >
                    {link}
                  </MuiLink>
                ))}
              </Stack>
            </Grid>

            {/* Contact Info */}
            <Grid item xs={12} sm={6} md={2}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                Contact
              </Typography>
              <Stack spacing={2}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <EmailIcon sx={{ fontSize: 18, opacity: 0.7 }} />
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    info@marketingiq.com
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <PhoneIcon sx={{ fontSize: 18, opacity: 0.7 }} />
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    +1 (555) 123-4567
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                  <LocationOnIcon sx={{ fontSize: 18, opacity: 0.7, mt: 0.3 }} />
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    123 Tech Street<br />San Francisco, CA 94105
                  </Typography>
                </Box>
              </Stack>
            </Grid>
          </Grid>

          <Divider sx={{ my: 4, borderColor: 'rgba(255,255,255,0.1)' }} />

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
            <Typography variant="body2" sx={{ opacity: 0.6 }}>
              © 2025 Marketing IQ. All rights reserved.
            </Typography>
            <Stack direction="row" spacing={3}>
              <MuiLink
                sx={{
                  color: 'rgba(255,255,255,0.6)',
                  textDecoration: 'none',
                  fontSize: '0.875rem',
                  '&:hover': { color: 'white' },
                  cursor: 'pointer',
                }}
              >
                Privacy Policy
              </MuiLink>
              <MuiLink
                sx={{
                  color: 'rgba(255,255,255,0.6)',
                  textDecoration: 'none',
                  fontSize: '0.875rem',
                  '&:hover': { color: 'white' },
                  cursor: 'pointer',
                }}
              >
                Terms of Service
              </MuiLink>
              <MuiLink
                sx={{
                  color: 'rgba(255,255,255,0.6)',
                  textDecoration: 'none',
                  fontSize: '0.875rem',
                  '&:hover': { color: 'white' },
                  cursor: 'pointer',
                }}
              >
                Cookie Policy
              </MuiLink>
            </Stack>
          </Box>
        </Container>
      </Box>
    </Box>
  );
};
