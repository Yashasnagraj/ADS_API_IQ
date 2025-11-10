import React from 'react';
import { Box, Typography, Button, Card } from '@mui/material';
import SearchOffIcon from '@mui/icons-material/SearchOff';
import FolderOffIcon from '@mui/icons-material/FolderOff';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import { colors } from '../../theme/designTokens';

interface EmptyStateProps {
  title?: string;
  description?: string;
  icon?: 'search' | 'folder' | 'error' | 'ai' | React.ReactNode;
  actionLabel?: string;
  onAction?: () => void;
  secondaryActionLabel?: string;
  onSecondaryAction?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = 'No data available',
  description = 'There is no data to display at the moment.',
  icon = 'folder',
  actionLabel,
  onAction,
  secondaryActionLabel,
  onSecondaryAction,
}) => {
  // Get icon component
  const renderIcon = () => {
    if (React.isValidElement(icon)) {
      return icon;
    }

    const iconProps = {
      sx: {
        fontSize: 80,
        color: colors.gray[300],
        mb: 2,
      },
    };

    switch (icon) {
      case 'search':
        return <SearchOffIcon {...iconProps} />;
      case 'error':
        return <ErrorOutlineIcon {...iconProps} />;
      case 'ai':
        return <AutoAwesomeIcon {...iconProps} sx={{ ...iconProps.sx, color: colors.primary.main }} />;
      default:
        return <FolderOffIcon {...iconProps} />;
    }
  };

  return (
    <Card
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        p: 6,
        textAlign: 'center',
        minHeight: 400,
        border: `2px dashed ${colors.gray[200]}`,
        boxShadow: 'none',
        bgcolor: colors.gray[50],
      }}
    >
      <Box sx={{ maxWidth: 400 }}>
        {renderIcon()}

        <Typography
          variant="h5"
          sx={{
            fontWeight: 600,
            color: colors.text.primary,
            mb: 1,
          }}
        >
          {title}
        </Typography>

        <Typography
          variant="body1"
          sx={{
            color: colors.text.secondary,
            mb: 3,
          }}
        >
          {description}
        </Typography>

        {(actionLabel || secondaryActionLabel) && (
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
            {actionLabel && onAction && (
              <Button variant="contained" onClick={onAction} size="large">
                {actionLabel}
              </Button>
            )}
            {secondaryActionLabel && onSecondaryAction && (
              <Button variant="outlined" onClick={onSecondaryAction} size="large">
                {secondaryActionLabel}
              </Button>
            )}
          </Box>
        )}
      </Box>
    </Card>
  );
};

export default EmptyState;
