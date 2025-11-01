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
  IconButton,
  ListSubheader,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import { useNavigate, useLocation } from 'react-router-dom';
import { GlobalFilterBar } from './GlobalFilterBar';
import { useFilters } from '../../context/FilterContext';
import { FloatingChatButton } from '../chat/FloatingChatButton';

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
        { text: 'Unified Dashboard', path: '/dashboard/unified' },
        { text: 'Google Ads', path: '/dashboard/google-ads' },
        { text: 'Meta Ads', path: '/dashboard/meta-ads' },
        { text: 'Google Analytics', path: '/dashboard/ga4' },
        { text: 'E-Commerce', path: '/dashboard/ecommerce' },
      ],
    },
    {
      title: 'Data Agent',
      items: [
        { text: 'Campaigns', path: '/dashboard/data/campaigns' },
        { text: 'Keywords', path: '/dashboard/data/keywords' },
        { text: 'Ad Groups', path: '/dashboard/data/adgroups' },
      ],
    },
    {
      title: 'Insight Agent',
      items: [
        { text: 'Insights Summary', path: '/dashboard/insights/summary' },
        { text: 'Anomaly Detection', path: '/dashboard/insights/anomalies' },
        { text: 'Campaign Insights', path: '/dashboard/insights/campaigns' },
      ],
    },
    {
      title: 'Optimization Agent',
      items: [
        { text: 'Budget Optimizer', path: '/dashboard/optimization/budget' },
        { text: 'Keyword Optimizer', path: '/dashboard/optimization/keywords' },
        { text: 'Campaign Simulator', path: '/dashboard/optimization/simulator' },
      ],
    },
    {
      title: 'Forecasting Agent',
      items: [
        { text: 'CTR Forecast', path: '/dashboard/forecasting/ctr' },
        { text: 'Spend Forecast', path: '/dashboard/forecasting/spend' },
        { text: 'Scenario Simulator', path: '/dashboard/forecasting/scenarios' },
      ],
    },
    {
      title: 'Alert Agent',
      items: [
        { text: 'Alerts Dashboard', path: '/dashboard/alerts/dashboard' },
        { text: 'Thresholds Monitor', path: '/dashboard/alerts/thresholds' },
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
