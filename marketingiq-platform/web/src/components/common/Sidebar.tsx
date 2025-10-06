import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Collapse,
  Typography,
  Box,
  useTheme,
  Divider,
} from '@mui/material';
import {
  Dashboard,
  Campaign,
  GroupWork,
  Tag,
  Search,
  Memory,
  Insights,
  BubbleChart,
  Warning,
  AutoGraph,
  AttachMoney,
  TrendingUp,
  Timeline,
  Speed,
  Science,
  NotificationImportant,
  MonitorHeart,
  ExpandLess,
  ExpandMore,
  Home,
  SpaceDashboard,
} from '@mui/icons-material';

interface SidebarProps {
  open: boolean;
  onToggle: () => void;
}

interface MenuItem {
  title: string;
  icon: React.ReactElement;
  path?: string;
  children?: { title: string; path: string; icon: React.ReactElement }[];
}

const Sidebar: React.FC<SidebarProps> = ({ open }) => {
  const location = useLocation();
  const theme = useTheme();
  const [expandedItems, setExpandedItems] = React.useState<string[]>(['Data Agent', 'Insight Agent']);
  const [isHovered, setIsHovered] = React.useState(false);

  const handleExpandClick = (title: string) => {
    setExpandedItems((prev) =>
      prev.includes(title)
        ? prev.filter((item) => item !== title)
        : [...prev, title]
    );
  };

  const menuItems: MenuItem[] = [
    {
      title: 'Command Center',
      icon: <Home />,
      path: '/',
    },
    {
      title: 'Unified Dashboard',
      icon: <SpaceDashboard />,
      path: '/dashboard',
    },
    {
      title: 'Data Agent',
      icon: <Dashboard />,
      children: [
        { title: 'Campaigns', path: '/data/campaigns', icon: <Campaign /> },
        { title: 'Ad Groups', path: '/data/adgroups', icon: <GroupWork /> },
        { title: 'Keywords', path: '/data/keywords', icon: <Tag /> },
        { title: 'Search Terms', path: '/data/search-terms', icon: <Search /> },
        { title: 'ML Features', path: '/data/ml-features', icon: <Memory /> },
      ],
    },
    {
      title: 'Insight Agent',
      icon: <Insights />,
      children: [
        { title: 'Campaign Insights', path: '/insights/campaigns', icon: <AutoGraph /> },
        { title: 'Keyword Insights', path: '/insights/keywords', icon: <BubbleChart /> },
        { title: 'Anomaly Detection', path: '/insights/anomalies', icon: <Warning /> },
        { title: 'Summary', path: '/insights/summary', icon: <AutoGraph /> },
      ],
    },
    {
      title: 'Optimization Agent',
      icon: <Speed />,
      children: [
        { title: 'Budget Optimizer', path: '/optimization/budget', icon: <AttachMoney /> },
        { title: 'Keyword Optimizer', path: '/optimization/keywords', icon: <TrendingUp /> },
        { title: 'Campaign Simulator', path: '/optimization/simulator', icon: <Science /> },
      ],
    },
    {
      title: 'Forecasting Agent',
      icon: <Timeline />,
      children: [
        { title: 'CTR Forecast', path: '/forecasting/ctr', icon: <TrendingUp /> },
        { title: 'Spend Forecast', path: '/forecasting/spend', icon: <AttachMoney /> },
        { title: 'Scenario Simulator', path: '/forecasting/scenarios', icon: <Science /> },
      ],
    },
    {
      title: 'Alert Agent',
      icon: <NotificationImportant />,
      children: [
        { title: 'Thresholds Monitor', path: '/alerts/thresholds', icon: <MonitorHeart /> },
        { title: 'Alerts Dashboard', path: '/alerts/dashboard', icon: <Warning /> },
      ],
    },
  ];

  const sidebarWidth = isHovered ? 240 : 64;

  return (
    <Drawer
      variant="permanent"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      sx={{
        width: sidebarWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: sidebarWidth,
          boxSizing: 'border-box',
          bgcolor: 'background.paper',
          borderRight: `1px solid ${theme.palette.divider}`,
          transition: theme.transitions.create('width', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.shorter,
          }),
          overflowX: 'hidden',
        },
      }}
    >
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Typography
          variant="h6"
          sx={{
            fontWeight: 700,
            background: 'linear-gradient(90deg, #00bcd4 0%, #4caf50 100%)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            display: isHovered ? 'block' : 'none',
            whiteSpace: 'nowrap',
          }}
        >
          MarketingIQ
        </Typography>
        {!isHovered && <Dashboard sx={{ color: 'primary.main' }} />}
      </Box>
      <Divider />
      <List sx={{ px: 1, mt: 1 }}>
        {menuItems.map((item) => (
          <Box key={item.title}>
            <ListItem disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                {...(item.path && !item.children ? { component: Link, to: item.path } : {})}
                onClick={() => item.children && handleExpandClick(item.title)}
                selected={!!(item.path && !item.children && location.pathname === item.path)}
                sx={{
                  borderRadius: 1,
                  '&.Mui-selected': {
                    bgcolor: 'primary.main',
                    color: 'background.default',
                    '&:hover': {
                      bgcolor: 'primary.dark',
                    },
                    '& .MuiListItemIcon-root': {
                      color: 'background.default',
                    },
                  },
                  '&:hover': {
                    bgcolor: 'action.hover',
                  },
                }}
              >
                <ListItemIcon sx={{ minWidth: 40, color: 'primary.main' }}>
                  {item.icon}
                </ListItemIcon>
                {isHovered && (
                  <>
                    <ListItemText
                      primary={item.title}
                      primaryTypographyProps={{
                        fontSize: '0.875rem',
                        fontWeight: 500,
                        whiteSpace: 'nowrap',
                      }}
                    />
                    {item.children &&
                      (expandedItems.includes(item.title) ? <ExpandLess /> : <ExpandMore />)}
                  </>
                )}
              </ListItemButton>
            </ListItem>
            {isHovered && item.children && (
              <Collapse in={expandedItems.includes(item.title)} timeout="auto" unmountOnExit>
                <List component="div" disablePadding>
                  {item.children.map((child) => (
                    <ListItem key={child.path} disablePadding sx={{ pl: 2, mb: 0.25 }}>
                      <ListItemButton
                        component={Link}
                        to={child.path}
                        selected={location.pathname === child.path}
                        sx={{
                          borderRadius: 1,
                          '&.Mui-selected': {
                            bgcolor: 'primary.main',
                            color: 'background.default',
                            '&:hover': {
                              bgcolor: 'primary.dark',
                            },
                            '& .MuiListItemIcon-root': {
                              color: 'background.default',
                            },
                          },
                          '&:hover': {
                            bgcolor: 'action.hover',
                          },
                        }}
                      >
                        <ListItemIcon sx={{ minWidth: 36, fontSize: '1rem' }}>
                          {child.icon}
                        </ListItemIcon>
                        <ListItemText
                          primary={child.title}
                          primaryTypographyProps={{
                            fontSize: '0.813rem',
                            whiteSpace: 'nowrap',
                          }}
                        />
                      </ListItemButton>
                    </ListItem>
                  ))}
                </List>
              </Collapse>
            )}
          </Box>
        ))}
      </List>
    </Drawer>
  );
};

export default Sidebar;