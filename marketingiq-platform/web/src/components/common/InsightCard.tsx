// Insight Card Component - AI-Powered Insights
import React from 'react';
import { Paper, Typography, Box, Button, Chip, Stack } from '@mui/material';
import { motion } from 'framer-motion';
import { InsightData } from '../../types';

interface InsightCardProps {
  data: InsightData;
  index?: number;
}

export const InsightCard: React.FC<InsightCardProps> = ({ data, index = 0 }) => {
  const {
    type,
    title,
    insight,
    priority = 'info',
    details = [],
    actions = [],
    expectedImpact,
    confidence,
  } = data;

  const getTypeConfig = () => {
    switch (type) {
      case 'descriptive':
        return {
          title: title || 'What Happened',
          color: 'info.main',
          bgcolor: 'info.lighter',
        };
      case 'diagnostic':
        return {
          title: title || 'Why It Happened',
          color: 'warning.main',
          bgcolor: 'warning.lighter',
        };
      case 'prescriptive':
        return {
          title: title || 'What To Do',
          color: 'success.main',
          bgcolor: 'success.lighter',
        };
    }
  };

  const config = getTypeConfig();

  const getPriorityColor = () => {
    switch (priority) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'success';
      default:
        return 'info';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: type === 'prescriptive' ? 100 : type === 'descriptive' ? -100 : 0, y: type === 'diagnostic' ? 50 : 0 }}
      whileInView={{ opacity: 1, x: 0, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay: index * 0.2, duration: 0.6 }}
    >
      <Paper
        sx={{
          p: 3,
          borderLeft: 6,
          borderColor: `${getPriorityColor()}.main`,
          bgcolor: 'background.paper',
        }}
      >
        <Box display="flex" alignItems="center" gap={2} mb={2}>
          <Box
            sx={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              bgcolor: config.color,
            }}
          />
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            {config.title}
          </Typography>
        </Box>

        <Typography variant="body1" sx={{ mb: details.length > 0 ? 2 : 3, lineHeight: 1.7 }}>
          {insight}
        </Typography>

        {details.length > 0 && (
          <Box sx={{ pl: 2, mb: 2 }}>
            {details.map((detail, i) => (
              <Typography key={i} variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                • {detail}
              </Typography>
            ))}
          </Box>
        )}

        {(expectedImpact || confidence) && (
          <Stack direction="row" spacing={1} mb={2}>
            {expectedImpact && (
              <Chip label={`Impact: ${expectedImpact}`} color="success" size="small" variant="outlined" />
            )}
            {confidence && (
              <Chip label={`Confidence: ${confidence}`} color="info" size="small" variant="outlined" />
            )}
          </Stack>
        )}

        {actions.length > 0 && (
          <Stack direction="row" spacing={2}>
            {actions.map((action, i) => (
              <Button
                key={i}
                variant={action.primary ? 'contained' : 'outlined'}
                onClick={action.onClick}
                size="small"
              >
                {action.label}
              </Button>
            ))}
          </Stack>
        )}
      </Paper>
    </motion.div>
  );
};

export default InsightCard;
