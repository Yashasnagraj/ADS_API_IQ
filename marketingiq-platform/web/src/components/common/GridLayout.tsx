import React from 'react';
import { Box } from '@mui/material';

interface GridLayoutProps {
  children: React.ReactNode;
  columns?: number;
  spacing?: number;
}

export const GridContainer: React.FC<GridLayoutProps> = ({ children, spacing = 3 }) => {
  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(0, 1fr))',
        gap: spacing,
        mb: 3,
      }}
    >
      {children}
    </Box>
  );
};

interface GridItemProps {
  children: React.ReactNode;
  xs?: number;
  sm?: number;
  md?: number;
  lg?: number;
}

export const GridItem: React.FC<GridItemProps> = ({
  children,
  xs = 12,
  sm,
  md,
  lg
}) => {
  return (
    <Box
      sx={{
        gridColumn: {
          xs: `span ${xs}`,
          sm: sm ? `span ${sm}` : undefined,
          md: md ? `span ${md}` : undefined,
          lg: lg ? `span ${lg}` : undefined,
        },
      }}
    >
      {children}
    </Box>
  );
};