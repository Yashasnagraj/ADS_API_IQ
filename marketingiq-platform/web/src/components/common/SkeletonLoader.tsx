import React from 'react';
import { Box, Skeleton, Card, CardContent, Grid } from '@mui/material';

interface SkeletonLoaderProps {
  variant?: 'kpi' | 'table' | 'chart' | 'card' | 'list';
  count?: number;
}

export const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({ variant = 'card', count = 1 }) => {
  // KPI Card Skeleton
  if (variant === 'kpi') {
    return (
      <Grid container spacing={3}>
        {Array.from({ length: count }).map((_, index) => (
          <Grid item xs={12} sm={6} md={2} key={index}>
            <Card sx={{ height: 120 }}>
              <CardContent>
                <Skeleton variant="text" width="60%" height={20} sx={{ mb: 1 }} />
                <Skeleton variant="text" width="80%" height={32} sx={{ mb: 1 }} />
                <Skeleton variant="text" width="40%" height={16} />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  }

  // Table Skeleton
  if (variant === 'table') {
    return (
      <Box sx={{ width: '100%' }}>
        <Skeleton variant="rectangular" width="100%" height={48} sx={{ mb: 1 }} />
        {Array.from({ length: count }).map((_, index) => (
          <Skeleton key={index} variant="rectangular" width="100%" height={52} sx={{ mb: 0.5 }} />
        ))}
      </Box>
    );
  }

  // Chart Skeleton
  if (variant === 'chart') {
    return (
      <Card>
        <CardContent>
          <Skeleton variant="text" width="40%" height={28} sx={{ mb: 2 }} />
          <Skeleton variant="rectangular" width="100%" height={300} />
          <Box sx={{ display: 'flex', gap: 2, mt: 2, justifyContent: 'center' }}>
            <Skeleton variant="text" width={80} height={20} />
            <Skeleton variant="text" width={80} height={20} />
            <Skeleton variant="text" width={80} height={20} />
          </Box>
        </CardContent>
      </Card>
    );
  }

  // List Skeleton
  if (variant === 'list') {
    return (
      <Box>
        {Array.from({ length: count }).map((_, index) => (
          <Box
            key={index}
            sx={{
              display: 'flex',
              gap: 2,
              alignItems: 'center',
              mb: 2,
              p: 2,
              border: '1px solid #e0e0e0',
              borderRadius: 2,
            }}
          >
            <Skeleton variant="circular" width={40} height={40} />
            <Box sx={{ flex: 1 }}>
              <Skeleton variant="text" width="60%" height={24} />
              <Skeleton variant="text" width="40%" height={20} />
            </Box>
          </Box>
        ))}
      </Box>
    );
  }

  // Default Card Skeleton
  return (
    <Grid container spacing={3}>
      {Array.from({ length: count }).map((_, index) => (
        <Grid item xs={12} md={6} key={index}>
          <Card>
            <Skeleton variant="rectangular" width="100%" height={200} />
            <CardContent>
              <Skeleton variant="text" width="80%" height={28} sx={{ mb: 1 }} />
              <Skeleton variant="text" width="100%" height={20} sx={{ mb: 0.5 }} />
              <Skeleton variant="text" width="90%" height={20} sx={{ mb: 2 }} />
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Skeleton variant="rounded" width={80} height={32} />
                <Skeleton variant="rounded" width={80} height={32} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

export default SkeletonLoader;
