import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Paper,
  Chip,
  Button,
  Avatar,
  Fade,
  useTheme,
  alpha,
} from '@mui/material';
import {
  Psychology,
  ArrowUpward,
} from '@mui/icons-material';
import { animations } from './DashboardTemplate';

export interface AIInsight {
  type: 'opportunity' | 'warning' | 'prediction' | 'recommendation';
  title: string;
  description: string;
  impact: string;
  confidence: number;
  action: string;
  icon: React.ReactNode;
}

interface AIIntelligenceSectionProps {
  insights: AIInsight[];
  title?: string;
  subtitle?: string;
}

const AIIntelligenceSection: React.FC<AIIntelligenceSectionProps> = ({
  insights,
  title = 'AI Intelligence',
  subtitle = 'Machine learning insights and predictions based on your data',
}) => {
  const theme = useTheme();

  const getInsightColor = (type: string) => {
    switch (type) {
      case 'opportunity':
        return theme.palette.success.main;
      case 'warning':
        return theme.palette.warning.main;
      case 'prediction':
        return theme.palette.info.main;
      case 'recommendation':
        return theme.palette.primary.main;
      default:
        return theme.palette.text.primary;
    }
  };

  return (
    <Fade in timeout={1000}>
      <Card
        sx={{
          background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.03)} 0%, ${alpha(
            theme.palette.secondary.main,
            0.03
          )} 100%)`,
          borderTop: `3px solid ${theme.palette.primary.main}`,
        }}
      >
        <CardContent>
          <Box display="flex" alignItems="center" gap={2} mb={3}>
            <Avatar
              sx={{
                bgcolor: theme.palette.primary.main,
                width: 40,
                height: 40,
                animation: `${animations.float} 3s ease-in-out infinite`,
              }}
            >
              <Psychology />
            </Avatar>
            <Box>
              <Typography variant="h6" fontWeight="600">
                {title}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {subtitle}
              </Typography>
            </Box>
          </Box>

          <Grid container spacing={2}>
            {insights.map((insight, index) => (
              <Grid item xs={12} md={4} key={index}>
                <Paper
                  elevation={0}
                  sx={{
                    p: 2,
                    height: '100%',
                    border: `1px solid ${theme.palette.divider}`,
                    borderRadius: 2,
                    position: 'relative',
                    overflow: 'hidden',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: theme.shadows[4],
                      borderColor: theme.palette.primary.main,
                    },
                  }}
                >
                  <Box display="flex" alignItems="flex-start" gap={2}>
                    <Avatar
                      sx={{
                        bgcolor: alpha(getInsightColor(insight.type), 0.1),
                        color: getInsightColor(insight.type),
                        width: 36,
                        height: 36,
                      }}
                    >
                      {insight.icon}
                    </Avatar>
                    <Box flex={1}>
                      <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                        {insight.title}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" display="block" mb={1}>
                        {insight.description}
                      </Typography>
                      <Box display="flex" alignItems="center" justifyContent="space-between">
                        <Chip
                          label={insight.impact}
                          size="small"
                          sx={{
                            bgcolor: alpha(theme.palette.primary.main, 0.1),
                            color: theme.palette.primary.main,
                            fontWeight: 600,
                            fontSize: '0.7rem',
                          }}
                        />
                        <Typography variant="caption" color="text.secondary">
                          {insight.confidence}% confidence
                        </Typography>
                      </Box>
                      <Button
                        size="small"
                        variant="text"
                        sx={{ mt: 1, fontSize: '0.75rem' }}
                        endIcon={<ArrowUpward sx={{ fontSize: 14 }} />}
                      >
                        {insight.action}
                      </Button>
                    </Box>
                  </Box>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    </Fade>
  );
};

export default AIIntelligenceSection;