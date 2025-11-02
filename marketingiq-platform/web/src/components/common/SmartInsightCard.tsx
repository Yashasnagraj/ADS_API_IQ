/**
 * Smart Insight Card - AI-Powered Insights Component
 *
 * Displays intelligent, actionable insights with visual hierarchy
 * Works across all dashboards
 */

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Button,
  Stack,
  Collapse,
  IconButton,
  Alert,
  AlertTitle,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  CheckCircle,
  Warning,
  Error as ErrorIcon,
  Info,
  TrendingUp,
  TrendingDown,
  Lightbulb,
  ExpandMore,
  ExpandLess,
  PlayArrow,
} from '@mui/icons-material';

interface SmartInsightCardProps {
  type: 'success' | 'warning' | 'danger' | 'info';
  title: string;
  message: string;
  impact: string;
  confidence: number;
  actionable?: boolean;
  actions?: string[];
  index?: number;
}

export const SmartInsightCard: React.FC<SmartInsightCardProps> = ({
  type,
  title,
  message,
  impact,
  confidence,
  actionable = false,
  actions = [],
  index = 0,
}) => {
  const [expanded, setExpanded] = React.useState(false);

  const getTypeConfig = () => {
    switch (type) {
      case 'success':
        return {
          icon: <CheckCircle />,
          color: '#10b981',
          bgcolor: '#10b98110',
          borderColor: '#10b981',
          severity: 'success' as const,
        };
      case 'warning':
        return {
          icon: <Warning />,
          color: '#f59e0b',
          bgcolor: '#f59e0b10',
          borderColor: '#f59e0b',
          severity: 'warning' as const,
        };
      case 'danger':
        return {
          icon: <ErrorIcon />,
          color: '#ef4444',
          bgcolor: '#ef444410',
          borderColor: '#ef4444',
          severity: 'error' as const,
        };
      default:
        return {
          icon: <Info />,
          color: '#3b82f6',
          bgcolor: '#3b82f610',
          borderColor: '#3b82f6',
          severity: 'info' as const,
        };
    }
  };

  const config = getTypeConfig();

  return (
    <Card
      elevation={0}
      sx={{
        border: `2px solid ${config.borderColor}`,
        borderRadius: 2,
        background: config.bgcolor,
        transition: 'all 0.3s',
        animation: `fadeInUp 0.5s ease-out ${index * 0.1}s both`,
        '@keyframes fadeInUp': {
          from: {
            opacity: 0,
            transform: 'translateY(20px)',
          },
          to: {
            opacity: 1,
            transform: 'translateY(0)',
          },
        },
        '&:hover': {
          boxShadow: `0 8px 24px ${config.color}30`,
          transform: 'translateY(-2px)',
        },
      }}
    >
      <CardContent>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Box
              sx={{
                width: 40,
                height: 40,
                borderRadius: 2,
                bgcolor: config.color,
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              {config.icon}
            </Box>
            <Box>
              <Typography variant="h6" fontWeight={700} sx={{ color: config.color }}>
                {title}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                <Chip
                  label={`${confidence}% Confidence`}
                  size="small"
                  sx={{
                    bgcolor: `${config.color}20`,
                    color: config.color,
                    fontWeight: 600,
                    fontSize: '0.7rem',
                  }}
                />
                {actionable && (
                  <Chip
                    icon={<Lightbulb sx={{ fontSize: 14 }} />}
                    label="Actionable"
                    size="small"
                    sx={{
                      bgcolor: '#8b5cf620',
                      color: '#8b5cf6',
                      fontWeight: 600,
                      fontSize: '0.7rem',
                    }}
                  />
                )}
              </Box>
            </Box>
          </Box>
        </Box>

        {/* Message */}
        <Typography
          variant="body1"
          sx={{
            mb: 2,
            lineHeight: 1.7,
            color: 'text.primary',
            fontSize: '0.95rem',
          }}
        >
          {message}
        </Typography>

        {/* Impact */}
        <Alert
          severity={config.severity}
          icon={type === 'success' ? <TrendingUp /> : type === 'danger' ? <TrendingDown /> : <Info />}
          sx={{ mb: actions.length > 0 ? 2 : 0 }}
        >
          <AlertTitle sx={{ fontWeight: 700, fontSize: '0.9rem' }}>Expected Impact</AlertTitle>
          {impact}
        </Alert>

        {/* Actions */}
        {actions.length > 0 && (
          <Box>
            <Button
              variant="text"
              endIcon={expanded ? <ExpandLess /> : <ExpandMore />}
              onClick={() => setExpanded(!expanded)}
              sx={{
                color: config.color,
                fontWeight: 600,
                fontSize: '0.875rem',
                mb: 1,
              }}
            >
              {expanded ? 'Hide' : 'View'} Recommended Actions ({actions.length})
            </Button>
            <Collapse in={expanded}>
              <List dense sx={{ bgcolor: 'background.paper', borderRadius: 1, p: 1 }}>
                {actions.map((action, idx) => (
                  <ListItem
                    key={idx}
                    sx={{
                      py: 1,
                      borderBottom: idx < actions.length - 1 ? '1px solid' : 'none',
                      borderColor: 'divider',
                    }}
                  >
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <PlayArrow sx={{ color: config.color, fontSize: 20 }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={action}
                      primaryTypographyProps={{
                        fontSize: '0.875rem',
                        fontWeight: 500,
                      }}
                    />
                  </ListItem>
                ))}
              </List>
            </Collapse>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};
