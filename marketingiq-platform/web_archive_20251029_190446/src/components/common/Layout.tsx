import React, { useState } from 'react';
import { Box, useTheme } from '@mui/material';
import Sidebar from './Sidebar';
import Header from './Header';
import GlobalFilterBar from './GlobalFilterBar';
import FloatingChatbot from '../chatbot/FloatingChatbot';
import { useFilters } from '../../context/FilterContext';
import { useChat } from '../../context/ChatContext';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const theme = useTheme();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const { filters, setFilters } = useFilters();
  const { isChatOpen, chatPanelWidth } = useChat();

  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      <Sidebar open={sidebarOpen} onToggle={handleSidebarToggle} />
      <Box
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          marginRight: isChatOpen ? `${chatPanelWidth}px` : 0,
          transition: theme.transitions.create(['margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
        }}
      >
        <Header onSidebarToggle={handleSidebarToggle} sidebarOpen={sidebarOpen} />
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            p: 3,
            bgcolor: 'background.default',
          }}
        >
          {/* Global Filter Bar */}
          <GlobalFilterBar
            onFilterChange={setFilters}
            initialFilters={filters}
            compact={false}
          />

          {/* Main Content */}
          {children}
        </Box>
      </Box>

      {/* Floating AI Chatbot - Available on all pages */}
      <FloatingChatbot />
    </Box>
  );
};

export default Layout;