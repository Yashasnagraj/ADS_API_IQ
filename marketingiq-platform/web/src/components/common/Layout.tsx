// Layout Component with Sidebar Navigation
import React, { useState } from 'react';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  ListItem,
  ListItemButton,
  ListItemText,
  ListItemIcon,
  IconButton,
  ListSubheader,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import PsychologyIcon from '@mui/icons-material/Psychology';
import DashboardIcon from '@mui/icons-material/Dashboard';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import CampaignIcon from '@mui/icons-material/Campaign';
import SpellcheckIcon from '@mui/icons-material/Spellcheck';
import GroupWorkIcon from '@mui/icons-material/GroupWork';
import InsightsIcon from '@mui/icons-material/Insights';
import WarningIcon from '@mui/icons-material/Warning';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import TuneIcon from '@mui/icons-material/Tune';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import ViewQuiltIcon from '@mui/icons-material/ViewQuilt';
import NotificationsIcon from '@mui/icons-material/Notifications';
import SettingsIcon from '@mui/icons-material/Settings';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import DescriptionIcon from '@mui/icons-material/Description';
import BrushIcon from '@mui/icons-material/Brush';
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import { useNavigate, useLocation } from 'react-router-dom';
import { GlobalFilterBar } from './GlobalFilterBar';
import { useFilters } from '../../context/FilterContext';
import { FloatingChatButton } from '../chat/FloatingChatButton';
import { SiGoogleads, SiGoogleanalytics, SiFacebook } from 'react-icons/si';

const drawerWidth = 260;
const collapsedDrawerWidth = 65;

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { filters } = useFilters();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleSidebarToggle = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  const menuSections = [
    {
      title: 'Platform Dashboards',
      items: [
        { text: 'Unified Dashboard', path: '/dashboard/unified', icon: <DashboardIcon /> },
        { text: 'Google Ads', path: '/dashboard/google-ads', icon: <SiGoogleads /> },
        { text: 'Meta Ads', path: '/dashboard/meta-ads', icon: <SiFacebook /> },
        { text: 'Google Analytics', path: '/dashboard/ga4', icon: <SiGoogleanalytics /> },
        { text: 'E-Commerce', path: '/dashboard/ecommerce', icon: <ShoppingCartIcon /> },
      ],
    },
    {
      title: 'AI Intelligence ⭐',
      items: [
        { text: 'AI Ad Creator', path: '/ai/ad-creator', icon: <SmartToyIcon />, badge: 'NEW' },
        { text: 'AI Reports', path: '/ai/reports', icon: <DescriptionIcon />, badge: 'NEW' },
        { text: 'Creative Studio', path: '/ai/creative-studio', icon: <BrushIcon />, badge: 'NEW' },
        { text: 'Predictive Alerts', path: '/ai/predictive-alerts', icon: <NotificationsActiveIcon />, badge: 'NEW' },
        { text: 'Campaign Builder', path: '/ai/campaign-builder', icon: <RocketLaunchIcon />, badge: 'NEW' },
      ],
    },
    {
      title: 'Data Agent',
      items: [
        { text: 'Campaigns', path: '/dashboard/data/campaigns', icon: <CampaignIcon /> },
        { text: 'Keywords', path: '/dashboard/data/keywords', icon: <SpellcheckIcon /> },
        { text: 'Ad Groups', path: '/dashboard/data/adgroups', icon: <GroupWorkIcon /> },
      ],
    },
    {
      title: 'Insight Agent',
      items: [
        { text: 'Insights Summary', path: '/dashboard/insights/summary', icon: <InsightsIcon /> },
        { text: 'Anomaly Detection', path: '/dashboard/insights/anomalies', icon: <WarningIcon /> },
        { text: 'Campaign Insights', path: '/dashboard/insights/campaigns', icon: <AnalyticsIcon /> },
      ],
    },
    {
      title: 'Optimization Agent',
      items: [
        { text: 'Budget Optimizer', path: '/dashboard/optimization/budget', icon: <AccountBalanceIcon /> },
        { text: 'Keyword Optimizer', path: '/dashboard/optimization/keywords', icon: <TuneIcon /> },
        { text: 'Campaign Simulator', path: '/dashboard/optimization/simulator', icon: <PlayArrowIcon /> },
      ],
    },
    {
      title: 'Forecasting Agent',
      items: [
        { text: 'CTR Forecast', path: '/dashboard/forecasting/ctr', icon: <TrendingUpIcon /> },
        { text: 'Spend Forecast', path: '/dashboard/forecasting/spend', icon: <AttachMoneyIcon /> },
        { text: 'Scenario Simulator', path: '/dashboard/forecasting/scenarios', icon: <ViewQuiltIcon /> },
      ],
    },
    {
      title: 'Alert Agent',
      items: [
        { text: 'Alerts Dashboard', path: '/dashboard/alerts/dashboard', icon: <NotificationsIcon /> },
        { text: 'Thresholds Monitor', path: '/dashboard/alerts/thresholds', icon: <SettingsIcon /> },
      ],
    },
  ];

  const drawer = (
    <Box sx={{ overflow: 'auto', height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Toolbar sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', px: 2 }}>
        {!sidebarCollapsed ? (
          <Box
            onClick={() => navigate('/')}
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1.5,
              cursor: 'pointer',
              transition: 'all 0.3s',
              '&:hover': {
                transform: 'scale(1.02)',
                '& .logo-icon': {
                  transform: 'rotate(10deg)',
                }
              }
            }}
          >
            {/* Logo Icon */}
            <Box
              className="logo-icon"
              sx={{
                width: 40,
                height: 40,
                borderRadius: 2,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 4px 12px rgba(102, 126, 234, 0.4)',
                transition: 'transform 0.3s',
              }}
            >
              <PsychologyIcon sx={{ color: 'white', fontSize: 24 }} />
            </Box>

            {/* Brand Text */}
            <Box>
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 800,
                  fontSize: '1.1rem',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  letterSpacing: '-0.5px',
                  lineHeight: 1,
                }}
              >
                MarketingIQ
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  fontSize: '0.65rem',
                  color: 'text.secondary',
                  fontWeight: 600,
                  letterSpacing: '1px',
                  textTransform: 'uppercase',
                }}
              >
                AI Platform
              </Typography>
            </Box>
          </Box>
        ) : (
          <Box
            onClick={() => navigate('/')}
            sx={{
              width: 40,
              height: 40,
              borderRadius: 2,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 12px rgba(102, 126, 234, 0.4)',
              cursor: 'pointer',
              transition: 'all 0.3s',
              '&:hover': {
                transform: 'scale(1.1) rotate(10deg)',
              }
            }}
          >
            <PsychologyIcon sx={{ color: 'white', fontSize: 24 }} />
          </Box>
        )}
        <IconButton
          onClick={handleSidebarToggle}
          size="small"
          sx={{
            ml: sidebarCollapsed ? 0 : 'auto',
            color: 'text.secondary',
            '&:hover': {
              bgcolor: 'action.hover',
            }
          }}
        >
          {sidebarCollapsed ? <ChevronRightIcon /> : <ChevronLeftIcon />}
        </IconButton>
      </Toolbar>
      <Divider />
      {menuSections.map((section, sectionIndex) => (
        <List
          key={section.title}
          subheader={
            !sidebarCollapsed ? (
              <ListSubheader
                component="div"
                sx={{
                  bgcolor: 'background.paper',
                  fontWeight: 600,
                  fontSize: '0.75rem',
                  lineHeight: '2.5rem',
                  color: 'text.secondary',
                }}
              >
                {section.title}
              </ListSubheader>
            ) : undefined
          }
        >
          {section.items.map((item) => (
            <ListItem key={item.path} disablePadding>
              <ListItemButton
                selected={location.pathname === item.path}
                onClick={() => {
                  navigate(item.path);
                  setMobileOpen(false);
                }}
                sx={{
                  pl: sidebarCollapsed ? 2 : 3,
                  justifyContent: sidebarCollapsed ? 'center' : 'flex-start',
                  '&.Mui-selected': {
                    bgcolor: 'primary.light',
                    color: 'primary.contrastText',
                    '&:hover': {
                      bgcolor: 'primary.main',
                    },
                  },
                }}
                title={sidebarCollapsed ? item.text : ''}
              >
                {item.icon && (
                  <ListItemIcon
                    sx={{
                      minWidth: sidebarCollapsed ? 'auto' : 40,
                      color: location.pathname === item.path ? 'inherit' : 'text.secondary',
                      justifyContent: 'center',
                    }}
                  >
                    {item.icon}
                  </ListItemIcon>
                )}
                {!sidebarCollapsed && (
                  <ListItemText
                    primary={item.text}
                    primaryTypographyProps={{
                      fontSize: '0.875rem',
                    }}
                  />
                )}
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      ))}
    </Box>
  );

  const currentDrawerWidth = sidebarCollapsed ? collapsedDrawerWidth : drawerWidth;

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${currentDrawerWidth}px)` },
          ml: { sm: `${currentDrawerWidth}px` },
          transition: 'width 0.3s, margin 0.3s',
        }}
      >
        <Toolbar>
          {/* Mobile menu button */}
          <IconButton
            color="inherit"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>

          {/* Desktop expand button (only show when collapsed) */}
          {sidebarCollapsed && (
            <IconButton
              color="inherit"
              edge="start"
              onClick={handleSidebarToggle}
              sx={{ mr: 2, display: { xs: 'none', sm: 'block' } }}
            >
              <MenuIcon />
            </IconButton>
          )}

          <Typography variant="h6" noWrap component="div">
            Marketing Intelligence Platform
          </Typography>
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={{ width: { sm: currentDrawerWidth }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
            },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: currentDrawerWidth,
              transition: 'width 0.3s',
              overflowX: 'hidden',
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { sm: `calc(100% - ${currentDrawerWidth}px)` },
          minHeight: '100vh',
          bgcolor: 'background.default',
          transition: 'width 0.3s',
        }}
      >
        <Toolbar />
        <Box sx={{ p: 3 }}>
          <GlobalFilterBar
            compact={false}
            showPlatformFilter={false}
            showCampaignTypeFilter={true}
          />
          {children}
        </Box>
      </Box>

      {/* Floating Chat Button - AI Assistant */}
      <FloatingChatButton />
    </Box>
  );
};
