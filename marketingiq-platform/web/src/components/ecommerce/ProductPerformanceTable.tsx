/**
 * Product Performance Table Component
 * Shows product metrics with highlights for top/bottom performers
 */
import React from 'react';
import {
  Box,
  Typography,
  Chip,
  useTheme,
  alpha,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper
} from '@mui/material';
import { TrendingUp, TrendingDown, CheckCircle, Warning, Error } from '@mui/icons-material';
import { formatCurrency } from '../../utils/chartHelpers';

interface ProductMetrics {
  product_id: string;
  product_name: string;
  revenue: number;
  orders: number;
  conversion_rate: number;
  refund_rate: number;
  stock_status: string;
  rank: number;
}

interface ProductPerformanceTableProps {
  data: {
    products: ProductMetrics[];
    top_products: string[];
    bottom_products: string[];
    insight: string;
  } | null;
}

export const ProductPerformanceTable: React.FC<ProductPerformanceTableProps> = ({ data }) => {
  const theme = useTheme();

  if (!data || !data.products || data.products.length === 0) {
    return <Typography>No product data available</Typography>;
  }

  const { products, top_products, bottom_products, insight } = data;

  const getStockIcon = (status: string) => {
    switch (status) {
      case 'IN_STOCK':
        return <CheckCircle sx={{ fontSize: '1rem', color: '#10b981' }} />;
      case 'LOW_STOCK':
        return <Warning sx={{ fontSize: '1rem', color: '#f59e0b' }} />;
      case 'OUT_OF_STOCK':
        return <Error sx={{ fontSize: '1rem', color: '#ef4444' }} />;
      default:
        return null;
    }
  };

  return (
    <Box>
      <TableContainer component={Paper} sx={{ maxHeight: 400, boxShadow: 'none' }}>
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell sx={{ fontWeight: 700, background: alpha(theme.palette.primary.main, 0.05) }}>#</TableCell>
              <TableCell sx={{ fontWeight: 700, background: alpha(theme.palette.primary.main, 0.05) }}>Product</TableCell>
              <TableCell sx={{ fontWeight: 700, background: alpha(theme.palette.primary.main, 0.05) }}>Revenue</TableCell>
              <TableCell sx={{ fontWeight: 700, background: alpha(theme.palette.primary.main, 0.05) }}>Orders</TableCell>
              <TableCell sx={{ fontWeight: 700, background: alpha(theme.palette.primary.main, 0.05) }}>Conv. Rate</TableCell>
              <TableCell sx={{ fontWeight: 700, background: alpha(theme.palette.primary.main, 0.05) }}>Refund Rate</TableCell>
              <TableCell sx={{ fontWeight: 700, background: alpha(theme.palette.primary.main, 0.05) }}>Stock</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {products.map((product) => {
              const isTop = top_products.includes(product.product_name);
              const isBottom = bottom_products.includes(product.product_name);
              const isHighRefund = product.refund_rate > 10;

              return (
                <TableRow
                  key={product.product_id}
                  sx={{
                    '&:hover': { background: alpha(theme.palette.primary.main, 0.05) },
                    '&:last-child td': { borderBottom: 0 }
                  }}
                >
                  <TableCell sx={{ fontWeight: 600, color: theme.palette.text.secondary }}>
                    {product.rank}
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {isTop && <TrendingUp sx={{ fontSize: '1rem', color: '#10b981' }} />}
                      {isBottom && <TrendingDown sx={{ fontSize: '1rem', color: '#ef4444' }} />}
                      <Typography variant="body2" sx={{ fontWeight: isTop || isBottom ? 600 : 400 }}>
                        {product.product_name}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {formatCurrency(product.revenue)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">{product.orders}</Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={`${product.conversion_rate.toFixed(1)}%`}
                      size="small"
                      sx={{
                        background: alpha(theme.palette.success.main, 0.1),
                        color: theme.palette.success.dark,
                        fontWeight: 600
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={`${product.refund_rate.toFixed(1)}%`}
                      size="small"
                      sx={{
                        background: alpha(isHighRefund ? theme.palette.error.main : theme.palette.grey[500], 0.1),
                        color: isHighRefund ? theme.palette.error.dark : theme.palette.text.secondary,
                        fontWeight: 600
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      {getStockIcon(product.stock_status)}
                      <Typography variant="caption" sx={{ textTransform: 'capitalize' }}>
                        {product.stock_status.replace('_', ' ').toLowerCase()}
                      </Typography>
                    </Box>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Insight */}
      {insight && (
        <Box sx={{ mt: 2, p: 2, borderRadius: 1, background: alpha(theme.palette.info.main, 0.1) }}>
          <Chip label="AI Insight" size="small" sx={{ mb: 1 }} />
          <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>
            {insight}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default ProductPerformanceTable;
