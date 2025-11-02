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
import { useNavigate, useLocation } from 'react-router-dom';
import { GlobalFilterBar } from './GlobalFilterBar';
import { useFilters } from '../../context/FilterContext';
import { FloatingChatButton } from '../chat/FloatingChatButton';
import { SiGoogleads, SiGoogleanalytics, SiFacebook } from 'react-icons/si';

const drawerWidth = 260;

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { filters } = useFilters();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
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
    <Box sx={{ overflow: 'auto' }}>
      <Toolbar>
        <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 700 }}>
          MarketingIQ
        </Typography>
      </Toolbar>
      <Divider />
      {menuSections.map((section, sectionIndex) => (
        <List
          key={section.title}
          subheader={
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
                  pl: 3,
                  '&.Mui-selected': {
                    bgcolor: 'primary.light',
                    color: 'primary.contrastText',
                    '&:hover': {
                      bgcolor: 'primary.main',
                    },
                  },
                }}
              >
                {item.icon && (
                  <ListItemIcon
                    sx={{
                      minWidth: 40,
                      color: location.pathname === item.path ? 'inherit' : 'text.secondary',
                    }}
                  >
                    {item.icon}
                  </ListItemIcon>
                )}
                <ListItemText
                  primary={item.text}
                  primaryTypographyProps={{
                    fontSize: '0.875rem',
                  }}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      ))}
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div">
            Marketing Intelligence Platform
          </Typography>
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
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
              width: drawerWidth,
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
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          minHeight: '100vh',
          bgcolor: 'background.default',
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
