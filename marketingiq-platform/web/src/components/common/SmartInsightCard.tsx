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
    // Minimal color scheme - Only use subtle grays and one accent
    switch (type) {
      case 'success':
        return {
          icon: <CheckCircle />,
          color: '#1f2937', // Dark gray
          bgcolor: '#f9fafb', // Very light gray
          borderColor: '#e5e7eb', // Light gray border
          severity: 'success' as const,
        };
      case 'warning':
        return {
          icon: <Warning />,
          color: '#1f2937',
          bgcolor: '#fffbeb', // Subtle yellow tint
          borderColor: '#fef3c7',
          severity: 'warning' as const,
        };
      case 'danger':
        return {
          icon: <ErrorIcon />,
          color: '#1f2937',
          bgcolor: '#fef2f2', // Subtle red tint
          borderColor: '#fecaca',
          severity: 'error' as const,
        };
      default:
        return {
          icon: <Info />,
          color: '#1f2937',
          bgcolor: '#f9fafb',
          borderColor: '#e5e7eb',
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
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)',
          transform: 'translateY(-1px)',
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
                borderRadius: 1,
                bgcolor: '#f3f4f6',
                color: '#6b7280',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              {config.icon}
            </Box>
            <Box>
              <Typography variant="h6" fontWeight={600} sx={{ color: '#111827' }}>
                {title}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                <Chip
                  label={`${confidence}% Confidence`}
                  size="small"
                  sx={{
                    bgcolor: '#f3f4f6',
                    color: '#6b7280',
                    fontWeight: 500,
                    fontSize: '0.7rem',
                    border: '1px solid #e5e7eb',
                  }}
                />
                {actionable && (
                  <Chip
                    icon={<Lightbulb sx={{ fontSize: 14 }} />}
                    label="Actionable"
                    size="small"
                    sx={{
                      bgcolor: '#f3f4f6',
                      color: '#6b7280',
                      fontWeight: 500,
                      fontSize: '0.7rem',
                      border: '1px solid #e5e7eb',
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
                color: '#374151',
                fontWeight: 500,
                fontSize: '0.875rem',
                mb: 1,
              }}
            >
              {expanded ? 'Hide' : 'View'} Recommended Actions ({actions.length})
            </Button>
            <Collapse in={expanded}>
              <List dense sx={{ bgcolor: '#fafafa', borderRadius: 1, p: 1, border: '1px solid #e5e7eb' }}>
                {actions.map((action, idx) => (
                  <ListItem
                    key={idx}
                    sx={{
                      py: 1,
                      borderBottom: idx < actions.length - 1 ? '1px solid' : 'none',
                      borderColor: '#e5e7eb',
                    }}
                  >
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <PlayArrow sx={{ color: '#6b7280', fontSize: 20 }} />
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
