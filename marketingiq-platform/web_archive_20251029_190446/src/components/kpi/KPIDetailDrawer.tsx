/**
 * KPI Detail Drawer - Reusable drawer for showing KPI drill-down details
 * Displays detailed breakdown when user clicks on KPI cards
 */
import React from 'react';
import {
  Drawer,
  Box,
  Typography,
  IconButton,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  Button,
  useTheme,
  alpha,
  Avatar,
  LinearProgress,
} from '@mui/material';
import {
  Close,
  TrendingUp,
  TrendingDown,
  Error,
  Warning,
  Info,
  CheckCircle,
  ArrowForward,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';

export interface KPIDetailItem {
  id: string;
  name: string;
  value: number | string;
  status?: 'success' | 'warning' | 'error' | 'info';
  trend?: number;
  subtitle?: string;
  metadata?: Record<string, any>;
}

export interface KPIDetailDrawerProps {
  open: boolean;
  onClose: () => void;
  title: string;
  subtitle?: string;
  data: KPIDetailItem[];
  type?: 'list' | 'table' | 'anomaly' | 'alert';
  showTopCount?: number;
  trendData?: Array<{ date: string; value: number }>;
  color?: 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info';
  onAction?: (item: KPIDetailItem) => void;
  actionLabel?: string;
}

const KPIDetailDrawer: React.FC<KPIDetailDrawerProps> = ({
  open,
  onClose,
  title,
  subtitle,
  data,
  type = 'list',
  showTopCount = 10,
  trendData,
  color = 'primary',
  onAction,
  actionLabel = 'View',
}) => {
  const theme = useTheme();

  const colorMap = {
    primary: theme.palette.primary.main,
    secondary: theme.palette.secondary.main,
    success: theme.palette.success.main,
    error: theme.palette.error.main,
    warning: theme.palette.warning.main,
    info: theme.palette.info.main,
  };

  const selectedColor = colorMap[color];

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle sx={{ fontSize: 20, color: theme.palette.success.main }} />;
      case 'warning':
        return <Warning sx={{ fontSize: 20, color: theme.palette.warning.main }} />;
      case 'error':
        return <Error sx={{ fontSize: 20, color: theme.palette.error.main }} />;
      case 'info':
        return <Info sx={{ fontSize: 20, color: theme.palette.info.main }} />;
      default:
        return null;
    }
  };

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'success':
        return theme.palette.success.main;
      case 'warning':
        return theme.palette.warning.main;
      case 'error':
        return theme.palette.error.main;
      case 'info':
        return theme.palette.info.main;
      default:
        return theme.palette.text.primary;
    }
  };

  const displayData = data.slice(0, showTopCount);
  const hasMore = data.length > showTopCount;

  const renderList = () => (
    <List sx={{ width: '100%' }}>
      {displayData.map((item, index) => (
        <ListItem
          key={item.id}
          sx={{
            borderRadius: 2,
            mb: 1,
            transition: 'all 0.2s',
            '&:hover': {
              bgcolor: alpha(selectedColor, 0.05),
              transform: 'translateX(4px)',
            },
          }}
          secondaryAction={
            onAction && (
              <IconButton edge="end" onClick={() => onAction(item)}>
                <ArrowForward />
              </IconButton>
            )
          }
        >
          <ListItemIcon>
            {getStatusIcon(item.status) || (
              <Avatar
                sx={{
                  width: 32,
                  height: 32,
                  bgcolor: alpha(selectedColor, 0.1),
                  color: selectedColor,
                  fontSize: '0.875rem',
                }}
              >
                {index + 1}
              </Avatar>
            )}
          </ListItemIcon>
          <ListItemText
            primary={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="body1" fontWeight={500}>
                  {item.name}
                </Typography>
                {item.trend !== undefined && (
                  <Chip
                    icon={item.trend > 0 ? <TrendingUp sx={{ fontSize: 14 }} /> : <TrendingDown sx={{ fontSize: 14 }} />}
                    label={`${item.trend > 0 ? '+' : ''}${item.trend}%`}
                    size="small"
                    sx={{
                      height: 20,
                      fontSize: '0.7rem',
                      bgcolor: alpha(item.trend > 0 ? theme.palette.success.main : theme.palette.error.main, 0.1),
                      color: item.trend > 0 ? theme.palette.success.main : theme.palette.error.main,
                    }}
                  />
                )}
              </Box>
            }
            secondary={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                <Typography
                  variant="h6"
                  component="span"
                  sx={{
                    color: getStatusColor(item.status),
                    fontWeight: 600,
                  }}
                >
                  {item.value}
                </Typography>
                {item.subtitle && (
                  <Typography variant="caption" color="text.secondary">
                    {item.subtitle}
                  </Typography>
                )}
              </Box>
            }
          />
        </ListItem>
      ))}
    </List>
  );

  const renderTable = () => (
    <TableContainer component={Paper} elevation={0} sx={{ mt: 2 }}>
      <Table>
        <TableHead>
          <TableRow sx={{ bgcolor: alpha(selectedColor, 0.05) }}>
            <TableCell>Name</TableCell>
            <TableCell align="right">Value</TableCell>
            <TableCell align="center">Status</TableCell>
            {onAction && <TableCell align="center">Action</TableCell>}
          </TableRow>
        </TableHead>
        <TableBody>
          {displayData.map((item) => (
            <TableRow
              key={item.id}
              hover
              sx={{
                transition: 'all 0.2s',
                '&:hover': {
                  bgcolor: alpha(selectedColor, 0.03),
                },
              }}
            >
              <TableCell>
                <Typography variant="body2" fontWeight={500}>
                  {item.name}
                </Typography>
                {item.subtitle && (
                  <Typography variant="caption" color="text.secondary">
                    {item.subtitle}
                  </Typography>
                )}
              </TableCell>
              <TableCell align="right">
                <Typography variant="body2" fontWeight={600} color={getStatusColor(item.status)}>
                  {item.value}
                </Typography>
              </TableCell>
              <TableCell align="center">
                {item.status && (
                  <Chip
                    label={item.status}
                    size="small"
                    color={(item.status === 'success' || item.status === 'warning' || item.status === 'error' || item.status === 'info') ? item.status : 'default'}
                    variant="outlined"
                  />
                )}
              </TableCell>
              {onAction && (
                <TableCell align="center">
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={() => onAction(item)}
                    startIcon={<ArrowForward />}
                  >
                    {actionLabel}
                  </Button>
                </TableCell>
              )}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      PaperProps={{
        sx: {
          width: { xs: '100%', sm: 500 },
          p: 3,
        },
      }}
    >
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
        <Box>
          <Typography
            variant="h5"
            fontWeight="bold"
            sx={{
              background: `linear-gradient(135deg, ${selectedColor}, ${alpha(selectedColor, 0.6)})`,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            {title}
          </Typography>
          {subtitle && (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              {subtitle}
            </Typography>
          )}
        </Box>
        <IconButton onClick={onClose} size="small">
          <Close />
        </IconButton>
      </Box>

      <Divider sx={{ mb: 3 }} />

      {/* Summary */}
      <Alert
        severity="info"
        icon={<Info />}
        sx={{
          mb: 3,
          bgcolor: alpha(selectedColor, 0.05),
          borderLeft: `4px solid ${selectedColor}`,
        }}
      >
        <Typography variant="body2">
          Showing {displayData.length} of {data.length} total items
          {hasMore && ` (top ${showTopCount})`}
        </Typography>
      </Alert>

      {/* Trend Chart */}
      {trendData && trendData.length > 0 && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" fontWeight={600} gutterBottom>
            Trend Overview
          </Typography>
          <ResponsiveContainer width="100%" height={150}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke={alpha(theme.palette.divider, 0.3)} />
              <XAxis
                dataKey="date"
                stroke={theme.palette.text.secondary}
                tick={{ fontSize: 12 }}
                label={{ value: 'Date', position: 'insideBottom', offset: -5, fontSize: 12 }}
              />
              <YAxis
                stroke={theme.palette.text.secondary}
                tick={{ fontSize: 12 }}
                label={{ value: 'Value', angle: -90, position: 'insideLeft', fontSize: 12 }}
              />
              <RechartsTooltip
                contentStyle={{
                  backgroundColor: theme.palette.background.paper,
                  border: `1px solid ${theme.palette.divider}`,
                  borderRadius: 8,
                }}
              />
              <Line
                type="monotone"
                dataKey="value"
                stroke={selectedColor}
                strokeWidth={2}
                dot={{ fill: selectedColor, r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </Box>
      )}

      {/* Content */}
      <Box sx={{ flexGrow: 1, overflowY: 'auto' }}>
        {data.length === 0 ? (
          <Alert severity="info">No data available</Alert>
        ) : type === 'table' ? (
          renderTable()
        ) : (
          renderList()
        )}

        {hasMore && (
          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <Typography variant="caption" color="text.secondary">
              + {data.length - showTopCount} more items
            </Typography>
          </Box>
        )}
      </Box>
    </Drawer>
  );
};

export default KPIDetailDrawer;
