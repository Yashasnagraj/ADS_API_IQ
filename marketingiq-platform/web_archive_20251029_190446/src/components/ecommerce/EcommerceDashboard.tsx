/**
 * E-Commerce Performance Dashboard
 * All-in-one executive view showing complete business story
 */
import React, { useState } from 'react';
import {
  Box,
  Container,
  Grid,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Button,
  useTheme,
  alpha,
  Fade
} from '@mui/material';
import {
  MonetizationOn,
  ShoppingCart,
  TrendingUp,
  AttachMoney,
  Refresh as RefreshIcon,
  Download,
  People,
  ReportProblem
} from '@mui/icons-material';
import { useEcommerceOverview } from '../../hooks/useFilteredAPI';
import { EcommerceKPICard } from './EcommerceKPICard';
import { FunnelChart } from './FunnelChart';
import { ChannelPerformanceChart } from './ChannelPerformanceChart';
import { ProductPerformanceTable } from './ProductPerformanceTable';
import { CustomerSegmentChart } from './CustomerSegmentChart';
import { ForecastAnomalyStrip } from './ForecastAnomalyStrip';

export const EcommerceDashboard: React.FC = () => {
  const theme = useTheme();
  const { data, loading, error, refetch } = useEcommerceOverview();

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '80vh' }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">
          Failed to load e-commerce data: {error.message}
        </Alert>
      </Container>
    );
  }

  const kpis = data?.kpis;
  const funnel = data?.funnel;
  const channels = data?.channels;
  const products = data?.products;
  const segments = data?.segments;
  const forecast = data?.forecast;
  const anomalies = data?.anomalies;

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.02)} 0%, ${alpha(theme.palette.background.default, 1)} 100%)`,
        pb: 4
      }}
    >
      {/* Header */}
      <Box
        sx={{
          background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
          color: 'white',
          py: 4,
          px: 3,
          mb: 4,
          boxShadow: `0 8px 32px ${alpha(theme.palette.primary.main, 0.3)}`
        }}
      >
        <Container maxWidth="xl">
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box>
              <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>
                E-Commerce Performance Dashboard
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                Complete business story from traffic to sales
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={() => refetch()}
                sx={{
                  color: '#ffffff',
                  borderColor: 'rgba(255, 255, 255, 0.5)',
                  '&:hover': {
                    borderColor: '#ffffff',
                    background: 'rgba(255, 255, 255, 0.1)'
                  }
                }}
              >
                Refresh
              </Button>
              <Button
                variant="contained"
                startIcon={<Download />}
                sx={{
                  background: '#ffffff',
                  color: theme.palette.primary.main,
                  '&:hover': {
                    background: 'rgba(255, 255, 255, 0.9)'
                  }
                }}
              >
                Export Report
              </Button>
            </Box>
          </Box>
        </Container>
      </Box>

      <Container maxWidth="xl">
        <Fade in timeout={600}>
          <Box>
            {/* 1️⃣ Header Summary KPIs */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
              <Grid item xs={12} sm={6} md={4} lg={2}>
                <EcommerceKPICard
                  title="Total Revenue"
                  value={kpis?.total_revenue || 0}
                  trend={kpis?.revenue_trend || 0}
                  format="currency"
                  icon={<MonetizationOn />}
                  color="#10b981"
                  tooltip="Total revenue from conversions"
                  delay={0}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={4} lg={2}>
                <EcommerceKPICard
                  title="Total Orders"
                  value={kpis?.total_orders || 0}
                  trend={kpis?.orders_trend || 0}
                  format="number"
                  icon={<ShoppingCart />}
                  color="#3b82f6"
                  tooltip="Total number of orders"
                  delay={100}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={4} lg={2}>
                <EcommerceKPICard
                  title="Conversion Rate"
                  value={kpis?.conversion_rate || 0}
                  trend={kpis?.cvr_trend || 0}
                  format="percentage"
                  icon={<TrendingUp />}
                  color="#8b5cf6"
                  tooltip="Overall conversion rate"
                  delay={200}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={4} lg={2}>
                <EcommerceKPICard
                  title="Avg Order Value"
                  value={kpis?.avg_order_value || 0}
                  trend={kpis?.aov_trend || 0}
                  format="currency"
                  icon={<AttachMoney />}
                  color="#f59e0b"
                  tooltip="Average order value (AOV)"
                  delay={300}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={4} lg={2}>
                <EcommerceKPICard
                  title="Returning Customers"
                  value={kpis?.returning_customer_rate || 0}
                  trend={0}
                  format="percentage"
                  icon={<People />}
                  color="#ec4899"
                  tooltip="% of returning customers"
                  delay={400}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={4} lg={2}>
                <EcommerceKPICard
                  title="Refund Rate"
                  value={kpis?.refund_rate || 0}
                  trend={0}
                  format="percentage"
                  icon={<ReportProblem />}
                  color="#ef4444"
                  tooltip="Product refund rate"
                  delay={500}
                />
              </Grid>
            </Grid>

            {/* 2️⃣ Funnel Visualization */}
            <Paper sx={{ p: 3, mb: 4, borderRadius: 2, boxShadow: theme.shadows[2] }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Conversion Funnel
              </Typography>
              <FunnelChart data={funnel} />
            </Paper>

            {/* 3️⃣ Channel Performance & 4️⃣ Product Performance */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
              <Grid item xs={12} lg={7}>
                <Paper sx={{ p: 3, height: '100%', borderRadius: 2, boxShadow: theme.shadows[2] }}>
                  <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                    Channel Performance
                  </Typography>
                  <ChannelPerformanceChart data={channels} />
                </Paper>
              </Grid>
              <Grid item xs={12} lg={5}>
                <Paper sx={{ p: 3, height: '100%', borderRadius: 2, boxShadow: theme.shadows[2] }}>
                  <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                    Customer Segments
                  </Typography>
                  <CustomerSegmentChart data={segments} />
                </Paper>
              </Grid>
            </Grid>

            {/* Product Performance Table */}
            <Paper sx={{ p: 3, mb: 4, borderRadius: 2, boxShadow: theme.shadows[2] }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Product Performance
              </Typography>
              <ProductPerformanceTable data={products} />
            </Paper>

            {/* 6️⃣ Forecast & Anomaly Strip */}
            <ForecastAnomalyStrip forecast={forecast} anomalies={anomalies} />
          </Box>
        </Fade>
      </Container>
    </Box>
  );
};

export default EcommerceDashboard;
