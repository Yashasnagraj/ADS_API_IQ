import { useSnackbar, VariantType } from 'notistack';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import WarningIcon from '@mui/icons-material/Warning';
import InfoIcon from '@mui/icons-material/Info';
import { colors } from '../../theme/designTokens';

export interface ToastOptions {
  variant?: VariantType;
  autoHideDuration?: number;
  anchorOrigin?: {
    vertical: 'top' | 'bottom';
    horizontal: 'left' | 'center' | 'right';
  };
}

export const useToast = () => {
  const { enqueueSnackbar, closeSnackbar } = useSnackbar();

  const showToast = (message: string, options?: ToastOptions) => {
    return enqueueSnackbar(message, {
      variant: options?.variant || 'default',
      autoHideDuration: options?.autoHideDuration || 5000,
      anchorOrigin: options?.anchorOrigin || {
        vertical: 'top',
        horizontal: 'right',
      },
    });
  };

  const success = (message: string, duration?: number) => {
    return showToast(message, {
      variant: 'success',
      autoHideDuration: duration,
    });
  };

  const error = (message: string, duration?: number) => {
    return showToast(message, {
      variant: 'error',
      autoHideDuration: duration || 7000,
    });
  };

  const warning = (message: string, duration?: number) => {
    return showToast(message, {
      variant: 'warning',
      autoHideDuration: duration || 6000,
    });
  };

  const info = (message: string, duration?: number) => {
    return showToast(message, {
      variant: 'info',
      autoHideDuration: duration,
    });
  };

  const dismiss = (key?: string | number) => {
    if (key) {
      closeSnackbar(key);
    } else {
      closeSnackbar();
    }
  };

  return {
    toast: showToast,
    success,
    error,
    warning,
    info,
    dismiss,
  };
};

// Styled components for toast variants
export const toastStyles = {
  default: {
    bgcolor: colors.gray[800],
    color: 'white',
  },
  success: {
    bgcolor: colors.success.main,
    color: 'white',
    icon: <CheckCircleIcon sx={{ mr: 1 }} />,
  },
  error: {
    bgcolor: colors.error.main,
    color: 'white',
    icon: <ErrorIcon sx={{ mr: 1 }} />,
  },
  warning: {
    bgcolor: colors.warning.main,
    color: 'white',
    icon: <WarningIcon sx={{ mr: 1 }} />,
  },
  info: {
    bgcolor: colors.info.main,
    color: 'white',
    icon: <InfoIcon sx={{ mr: 1 }} />,
  },
};

export default useToast;
