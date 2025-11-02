/**
 * Smart Insight Summary Banner
 * Shows aggregate statistics about AI-generated insights
 */

import React from 'react';
import { Paper, Typography, Box, Grid, Chip } from '@mui/material';
import { Psychology, TrendingUp, CheckCircle, Speed } from '@mui/icons-material';

interface SmartInsightSummaryProps {
  totalInsights: number;
  avgConfidence: number;
  highPriorityCount: number;
  actionableCount: number;
  isLoading?: boolean;
}

export const SmartInsightSummary: React.FC<SmartInsightSummaryProps> = ({
  totalInsights,
  avgConfidence,
  highPriorityCount,
  actionableCount,
  isLoading = false,
}) => {
  if (isLoading) {
    return (
      <Paper
        sx={{
          p: 2.5,
          mb: 3,
          background: 'linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%)',
          borderRadius: 2,
          border: '1px solid #e5e7eb',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Psychology
            sx={{
              fontSize: 28,
              color: '#6b7280',
              animation: 'pulse 1.5s ease-in-out infinite',
              '@keyframes pulse': {
                '0%, 100%': { opacity: 0.4 },
                '50%': { opacity: 1 },
              },
            }}
          />
          <Typography variant="body1" sx={{ color: '#6b7280', fontWeight: 500 }}>
            🧠 Generating Smart Insights...
          </Typography>
        </Box>
      </Paper>
    );
  }

  if (totalInsights === 0) {
    return null;
  }

  return (
    <Paper
      sx={{
        p: 2.5,
        mb: 3,
        background: 'linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%)',
        borderRadius: 2,
        border: '1px solid #e5e7eb',
        animation: 'fadeIn 0.5s ease-out',
        '@keyframes fadeIn': {
          from: { opacity: 0 },
          to: { opacity: 1 },
        },
      }}
    >
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
        <Psychology sx={{ fontSize: 28, color: '#374151' }} />
        <Box>
          <Typography variant="h6" fontWeight={600} sx={{ color: '#111827' }}>
            Smart Insight Summary
          </Typography>
          <Typography variant="caption" sx={{ color: '#6b7280' }}>
            AI detected <b>{totalInsights}</b> key opportunities with an average confidence of{' '}
            <b>{avgConfidence}%</b>
          </Typography>
        </Box>
      </Box>

      {/* Stats Grid */}
      <Grid container spacing={2}>
        <Grid item xs={6} sm={3}>
          <Box
            sx={{
              p: 1.5,
              bgcolor: '#ffffff',
              borderRadius: 1.5,
              border: '1px solid #e5e7eb',
              textAlign: 'center',
            }}
          >
            <Typography variant="h5" fontWeight={700} sx={{ color: '#111827', mb: 0.5 }}>
              {totalInsights}
            </Typography>
            <Typography variant="caption" sx={{ color: '#6b7280', fontWeight: 500 }}>
              Total Insights
            </Typography>
          </Box>
        </Grid>

        <Grid item xs={6} sm={3}>
          <Box
            sx={{
              p: 1.5,
              bgcolor: '#ffffff',
              borderRadius: 1.5,
              border: '1px solid #e5e7eb',
              textAlign: 'center',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, mb: 0.5 }}>
              <Typography variant="h5" fontWeight={700} sx={{ color: '#4CAF50' }}>
                {avgConfidence}%
              </Typography>
              <Speed sx={{ fontSize: 20, color: '#4CAF50' }} />
            </Box>
            <Typography variant="caption" sx={{ color: '#6b7280', fontWeight: 500 }}>
              Avg Confidence
            </Typography>
          </Box>
        </Grid>

        <Grid item xs={6} sm={3}>
          <Box
            sx={{
              p: 1.5,
              bgcolor: '#ffffff',
              borderRadius: 1.5,
              border: '1px solid #e5e7eb',
              textAlign: 'center',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, mb: 0.5 }}>
              <Typography variant="h5" fontWeight={700} sx={{ color: '#EF5350' }}>
                {highPriorityCount}
              </Typography>
              <TrendingUp sx={{ fontSize: 20, color: '#EF5350' }} />
            </Box>
            <Typography variant="caption" sx={{ color: '#6b7280', fontWeight: 500 }}>
              High Priority
            </Typography>
          </Box>
        </Grid>

        <Grid item xs={6} sm={3}>
          <Box
            sx={{
              p: 1.5,
              bgcolor: '#ffffff',
              borderRadius: 1.5,
              border: '1px solid #e5e7eb',
              textAlign: 'center',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, mb: 0.5 }}>
              <Typography variant="h5" fontWeight={700} sx={{ color: '#42A5F5' }}>
                {actionableCount}
              </Typography>
              <CheckCircle sx={{ fontSize: 20, color: '#42A5F5' }} />
            </Box>
            <Typography variant="caption" sx={{ color: '#6b7280', fontWeight: 500 }}>
              Actionable
            </Typography>
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );
};
