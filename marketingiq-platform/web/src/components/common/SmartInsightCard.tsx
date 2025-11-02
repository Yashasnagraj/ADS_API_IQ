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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
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
  Launch,
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
  impactScore?: number; // 0-100 for visualization
  whyItMatters?: string; // Contextual explanation
  category?: 'Performance' | 'Spend' | 'Conversion' | 'General';
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
  impactScore = 70,
  whyItMatters,
  category = 'General',
}) => {
  const [expanded, setExpanded] = React.useState(false);
  const [dialogOpen, setDialogOpen] = React.useState(false);

  const getTypeConfig = () => {
    // Minimal color scheme - subtle border-left accents only
    switch (type) {
      case 'success':
        return {
          icon: <CheckCircle />,
          color: '#1f2937',
          bgcolor: '#fafafa',
          borderColor: '#e5e7eb',
          borderLeftColor: '#4CAF50', // Subtle green accent
          severity: 'success' as const,
          impactColor: '#4CAF50',
        };
      case 'warning':
        return {
          icon: <Warning />,
          color: '#1f2937',
          bgcolor: '#fafafa',
          borderColor: '#e5e7eb',
          borderLeftColor: '#FFA726', // Subtle orange accent
          severity: 'warning' as const,
          impactColor: '#FFA726',
        };
      case 'danger':
        return {
          icon: <ErrorIcon />,
          color: '#1f2937',
          bgcolor: '#fafafa',
          borderColor: '#e5e7eb',
          borderLeftColor: '#EF5350', // Subtle red accent
          severity: 'error' as const,
          impactColor: '#EF5350',
        };
      default:
        return {
          icon: <Info />,
          color: '#1f2937',
          bgcolor: '#fafafa',
          borderColor: '#e5e7eb',
          borderLeftColor: '#42A5F5', // Subtle blue accent
          severity: 'info' as const,
          impactColor: '#42A5F5',
        };
    }
  };

  const config = getTypeConfig();

  return (
    <>
      <Card
        elevation={0}
        sx={{
          border: `1px solid ${config.borderColor}`,
          borderLeft: `5px solid ${config.borderLeftColor}`, // Trend-based color cue
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

        {/* Why it matters - Contextual explanation */}
        {whyItMatters && (
          <Box
            sx={{
              mb: 2,
              p: 1.5,
              bgcolor: '#f9fafb',
              borderRadius: 1,
              border: '1px solid #e5e7eb',
            }}
          >
            <Typography variant="caption" sx={{ fontWeight: 600, color: '#6b7280', display: 'block', mb: 0.5 }}>
              💡 Why this matters:
            </Typography>
            <Typography variant="body2" sx={{ color: '#374151', fontSize: '0.85rem', lineHeight: 1.6 }}>
              {whyItMatters}
            </Typography>
          </Box>
        )}

        {/* Impact Visualization */}
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
            <Typography variant="caption" sx={{ fontWeight: 600, color: '#6b7280' }}>
              Expected Impact
            </Typography>
            <Typography variant="caption" sx={{ fontWeight: 600, color: config.impactColor }}>
              {impact}
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={impactScore}
            sx={{
              height: 8,
              borderRadius: 5,
              bgcolor: '#e5e7eb',
              '& .MuiLinearProgress-bar': {
                bgcolor: config.impactColor,
                borderRadius: 5,
              },
            }}
          />
        </Box>

        {/* Actions */}
        {actions.length > 0 && (
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Button
              variant="text"
              endIcon={expanded ? <ExpandLess /> : <ExpandMore />}
              onClick={() => setExpanded(!expanded)}
              sx={{
                color: '#374151',
                fontWeight: 500,
                fontSize: '0.875rem',
              }}
            >
              {expanded ? 'Hide' : 'View'} Actions ({actions.length})
            </Button>
            {actionable && (
              <Button
                variant="outlined"
                size="small"
                endIcon={<Launch sx={{ fontSize: 16 }} />}
                onClick={() => setDialogOpen(true)}
                sx={{
                  borderColor: config.borderLeftColor,
                  color: config.borderLeftColor,
                  fontWeight: 500,
                  fontSize: '0.75rem',
                  '&:hover': {
                    borderColor: config.borderLeftColor,
                    bgcolor: `${config.borderLeftColor}10`,
                  },
                }}
              >
                View Details
              </Button>
            )}
          </Box>
        )}

        {/* Collapsible Actions List */}
        {actions.length > 0 && (
          <Collapse in={expanded}>
            <List dense sx={{ bgcolor: '#f9fafb', borderRadius: 1, p: 1, border: '1px solid #e5e7eb', mt: 1 }}>
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
        )}
      </CardContent>
    </Card>

    {/* Interactive Dialog for Detailed Recommendations */}
    <Dialog
      open={dialogOpen}
      onClose={() => setDialogOpen(false)}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 2,
          border: `2px solid ${config.borderLeftColor}`,
        },
      }}
    >
      <DialogTitle sx={{ borderBottom: '1px solid #e5e7eb', pb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Box
            sx={{
              width: 40,
              height: 40,
              borderRadius: 1,
              bgcolor: `${config.borderLeftColor}15`,
              color: config.borderLeftColor,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {config.icon}
          </Box>
          <Box>
            <Typography variant="h6" fontWeight={600}>
              {title}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Category: {category} • Confidence: {confidence}%
            </Typography>
          </Box>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ mt: 2 }}>
        {/* Message */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="body1" sx={{ lineHeight: 1.7, color: 'text.primary' }}>
            {message}
          </Typography>
        </Box>

        {/* Why it matters */}
        {whyItMatters && (
          <Box
            sx={{
              mb: 3,
              p: 2,
              bgcolor: '#f9fafb',
              borderRadius: 1,
              border: '1px solid #e5e7eb',
            }}
          >
            <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#111827', mb: 1 }}>
              💡 Why this matters
            </Typography>
            <Typography variant="body2" sx={{ color: '#374151', lineHeight: 1.6 }}>
              {whyItMatters}
            </Typography>
          </Box>
        )}

        {/* Impact Visualization */}
        <Box sx={{ mb: 3, p: 2, bgcolor: '#fafafa', borderRadius: 1, border: '1px solid #e5e7eb' }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#111827', mb: 2 }}>
            Impact Assessment
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Potential Impact
            </Typography>
            <Typography variant="body2" sx={{ fontWeight: 600, color: config.impactColor }}>
              {impactScore}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={impactScore}
            sx={{
              height: 10,
              borderRadius: 5,
              bgcolor: '#e5e7eb',
              '& .MuiLinearProgress-bar': {
                bgcolor: config.impactColor,
                borderRadius: 5,
              },
            }}
          />
          <Typography variant="caption" sx={{ display: 'block', mt: 1, color: 'text.secondary' }}>
            {impact}
          </Typography>
        </Box>

        {/* Recommended Actions */}
        {actions.length > 0 && (
          <Box>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#111827', mb: 1.5 }}>
              Recommended Actions
            </Typography>
            <List dense sx={{ bgcolor: '#f9fafb', borderRadius: 1, border: '1px solid #e5e7eb' }}>
              {actions.map((action, idx) => (
                <ListItem
                  key={idx}
                  sx={{
                    py: 1.5,
                    borderBottom: idx < actions.length - 1 ? '1px solid' : 'none',
                    borderColor: '#e5e7eb',
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 40 }}>
                    <Box
                      sx={{
                        width: 24,
                        height: 24,
                        borderRadius: '50%',
                        bgcolor: config.borderLeftColor,
                        color: 'white',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '0.75rem',
                        fontWeight: 600,
                      }}
                    >
                      {idx + 1}
                    </Box>
                  </ListItemIcon>
                  <ListItemText
                    primary={action}
                    primaryTypographyProps={{
                      fontSize: '0.9rem',
                      fontWeight: 500,
                    }}
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ borderTop: '1px solid #e5e7eb', p: 2 }}>
        <Button
          onClick={() => setDialogOpen(false)}
          sx={{
            color: '#6b7280',
            fontWeight: 500,
          }}
        >
          Close
        </Button>
        <Button
          variant="contained"
          sx={{
            bgcolor: config.borderLeftColor,
            fontWeight: 500,
            '&:hover': {
              bgcolor: config.borderLeftColor,
              opacity: 0.9,
            },
          }}
        >
          Apply Recommendations
        </Button>
      </DialogActions>
    </Dialog>
    </>
  );
};
