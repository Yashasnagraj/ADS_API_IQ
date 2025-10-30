import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Button,
  IconButton,
  Collapse,
  Fade,
  Grow,
  Tooltip,
  LinearProgress,
  useTheme,
  alpha,
} from '@mui/material';
import {
  LightbulbOutlined,
  TrendingUp,
  TrendingDown,
  Warning,
  CheckCircle,
  Info,
  ExpandMore,
  AutoFixHigh,
  Psychology,
  Timeline,
  Assignment,
} from '@mui/icons-material';
import { keyframes } from '@mui/system';

const pulse = keyframes`
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.8;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
`;

const slideIn = keyframes`
  from {
    transform: translateX(-20px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
`;

interface Insight {
  type: 'descriptive' | 'diagnostic' | 'predictive' | 'prescriptive';
  title: string;
  message: string;
  impact?: 'high' | 'medium' | 'low';
  confidence?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
  metrics?: {
    label: string;
    value: string | number;
    trend?: 'up' | 'down' | 'stable';
  }[];
}

interface InsightCardProps {
  insights: Insight[];
  title?: string;
  expandable?: boolean;
  animated?: boolean;
  onDismiss?: () => void;
}

const InsightCard: React.FC<InsightCardProps> = ({
  insights,
  title = 'AI-Powered Insights',
  expandable = true,
  animated = true,
  onDismiss,
}) => {
  const theme = useTheme();
  const [expanded, setExpanded] = React.useState(!expandable);
  const [visibleIndex, setVisibleIndex] = React.useState(0);

  React.useEffect(() => {
    if (animated && insights.length > 1) {
      const timer = setInterval(() => {
        setVisibleIndex((prev) => (prev + 1) % insights.length);
      }, 5000);
      return () => clearInterval(timer);
    }
  }, [insights.length, animated]);

  const getTypeIcon = (type: Insight['type']) => {
    switch (type) {
      case 'descriptive':
        return <Info sx={{ color: theme.palette.info.main }} />;
      case 'diagnostic':
        return <Psychology sx={{ color: theme.palette.warning.main }} />;
      case 'predictive':
        return <Timeline sx={{ color: theme.palette.primary.main }} />;
      case 'prescriptive':
        return <AutoFixHigh sx={{ color: theme.palette.success.main }} />;
    }
  };

  const getTypeColor = (type: Insight['type']) => {
    switch (type) {
      case 'descriptive':
        return 'info';
      case 'diagnostic':
        return 'warning';
      case 'predictive':
        return 'primary';
      case 'prescriptive':
        return 'success';
    }
  };

  const getImpactColor = (impact?: string) => {
    switch (impact) {
      case 'high':
        return theme.palette.error.main;
      case 'medium':
        return theme.palette.warning.main;
      case 'low':
        return theme.palette.success.main;
      default:
        return theme.palette.grey[500];
    }
  };

  return (
    <Card
      sx={{
        background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.05)} 0%, ${alpha(
          theme.palette.secondary.main,
          0.05
        )} 100%)`,
        border: `1px solid ${alpha(theme.palette.primary.main, 0.2)}`,
        transition: 'all 0.3s ease',
        animation: animated ? `${pulse} 3s infinite` : 'none',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: `0 8px 24px ${alpha(theme.palette.primary.main, 0.15)}`,
        },
      }}
    >
      <CardContent>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mb: 2,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <LightbulbOutlined
              sx={{
                color: theme.palette.primary.main,
                animation: `${pulse} 2s infinite`,
              }}
            />
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              {title}
            </Typography>
            {insights.length > 0 && (
              <Chip
                size="small"
                label={`${insights.length} insights`}
                color="primary"
                variant="outlined"
              />
            )}
          </Box>
          {expandable && (
            <IconButton
              onClick={() => setExpanded(!expanded)}
              sx={{
                transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
                transition: 'transform 0.3s',
              }}
            >
              <ExpandMore />
            </IconButton>
          )}
        </Box>

        <Collapse in={expanded} timeout="auto">
          {insights.map((insight, index) => (
            <Fade
              key={index}
              in={!animated || index === visibleIndex}
              timeout={600}
            >
              <Box
                sx={{
                  display: !animated || index === visibleIndex ? 'block' : 'none',
                  animation: `${slideIn} 0.5s ease`,
                }}
              >
                <Box
                  sx={{
                    p: 2,
                    mb: 2,
                    borderRadius: 2,
                    bgcolor: alpha(theme.palette.background.paper, 0.8),
                    border: `1px solid ${alpha(
                      theme.palette[getTypeColor(insight.type)].main,
                      0.3
                    )}`,
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      bgcolor: theme.palette.background.paper,
                      transform: 'scale(1.02)',
                    },
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    {getTypeIcon(insight.type)}
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                      {insight.title}
                    </Typography>
                    <Chip
                      size="small"
                      label={insight.type}
                      color={getTypeColor(insight.type) as any}
                      variant="outlined"
                      sx={{ fontSize: '0.7rem' }}
                    />
                    {insight.impact && (
                      <Chip
                        size="small"
                        label={`${insight.impact} impact`}
                        sx={{
                          bgcolor: alpha(getImpactColor(insight.impact), 0.1),
                          color: getImpactColor(insight.impact),
                          fontSize: '0.7rem',
                        }}
                      />
                    )}
                  </Box>

                  <Typography
                    variant="body2"
                    sx={{ mb: 2, color: theme.palette.text.secondary }}
                  >
                    {insight.message}
                  </Typography>

                  {insight.confidence !== undefined && (
                    <Box sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                        <Typography variant="caption">Confidence Level</Typography>
                        <Typography variant="caption" sx={{ fontWeight: 600 }}>
                          {Math.round(insight.confidence * 100)}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={insight.confidence * 100}
                        sx={{
                          height: 6,
                          borderRadius: 3,
                          bgcolor: alpha(theme.palette.primary.main, 0.1),
                          '& .MuiLinearProgress-bar': {
                            borderRadius: 3,
                            background: `linear-gradient(90deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
                          },
                        }}
                      />
                    </Box>
                  )}

                  {insight.metrics && insight.metrics.length > 0 && (
                    <Box sx={{ display: 'flex', gap: 2, mb: 2, flexWrap: 'wrap' }}>
                      {insight.metrics.map((metric, idx) => (
                        <Box
                          key={idx}
                          sx={{
                            flex: 1,
                            minWidth: 100,
                            p: 1,
                            borderRadius: 1,
                            bgcolor: alpha(theme.palette.primary.main, 0.05),
                            border: `1px solid ${alpha(theme.palette.primary.main, 0.1)}`,
                          }}
                        >
                          <Typography variant="caption" color="textSecondary">
                            {metric.label}
                          </Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                              {metric.value}
                            </Typography>
                            {metric.trend && (
                              <Box>
                                {metric.trend === 'up' && (
                                  <TrendingUp sx={{ fontSize: 16, color: theme.palette.success.main }} />
                                )}
                                {metric.trend === 'down' && (
                                  <TrendingDown sx={{ fontSize: 16, color: theme.palette.error.main }} />
                                )}
                              </Box>
                            )}
                          </Box>
                        </Box>
                      ))}
                    </Box>
                  )}

                  {insight.action && (
                    <Grow in timeout={500}>
                      <Button
                        variant="contained"
                        size="small"
                        startIcon={<Assignment />}
                        onClick={insight.action.onClick}
                        sx={{
                          background: `linear-gradient(45deg, ${theme.palette.primary.main} 30%, ${theme.palette.secondary.main} 90%)`,
                          boxShadow: `0 3px 5px 2px ${alpha(theme.palette.primary.main, 0.3)}`,
                          '&:hover': {
                            transform: 'scale(1.05)',
                            boxShadow: `0 4px 8px 2px ${alpha(theme.palette.primary.main, 0.4)}`,
                          },
                        }}
                      >
                        {insight.action.label}
                      </Button>
                    </Grow>
                  )}
                </Box>
              </Box>
            </Fade>
          ))}
        </Collapse>

        {animated && insights.length > 1 && (
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, mt: 2 }}>
            {insights.map((_, index) => (
              <Box
                key={index}
                sx={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  bgcolor: index === visibleIndex
                    ? theme.palette.primary.main
                    : alpha(theme.palette.primary.main, 0.3),
                  transition: 'all 0.3s',
                  cursor: 'pointer',
                }}
                onClick={() => setVisibleIndex(index)}
              />
            ))}
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default InsightCard;