import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Fab,
  Paper,
  IconButton,
  Typography,
  TextField,
  Avatar,
  CircularProgress,
  Chip,
  Fade,
  Slide,
  useTheme,
  alpha,
} from '@mui/material';
import {
  Chat as ChatIcon,
  Close as CloseIcon,
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import { API_CONFIG } from '../../config/api';
import { useFilters } from '../../context/FilterContext';
import { useChat } from '../../context/ChatContext';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const FloatingChatbot: React.FC = () => {
  const theme = useTheme();
  const { filters } = useFilters();
  const { isChatOpen, chatPanelWidth, setChatOpen, setChatPanelWidth } = useChat();
  const [isResizing, setIsResizing] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: '👋 Hi! I\'m your AI Marketing Assistant powered by Google Gemini. Ask me anything about your campaigns, keywords, or performance!',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const resizeHandleRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle resize drag
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isResizing) {
        const newWidth = window.innerWidth - e.clientX;
        setChatPanelWidth(Math.max(300, Math.min(800, newWidth)));
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
      document.body.style.cursor = 'default';
      document.body.style.userSelect = 'auto';
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing]);

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsResizing(true);
    e.preventDefault();
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Call the ADK chatbot API (port 8003)
      const response = await fetch(`${API_CONFIG.CHATBOT_API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
          customer_id: filters.customerId ? String(filters.customerId) : null,
          campaign_type: filters.campaignType !== 'ALL' ? filters.campaignType : null,
          date_range: filters.dateRange || null,
        }),
      });

      const data = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || 'Sorry, I encountered an error processing your request.',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '⚠️ Sorry, I\'m having trouble connecting to the ADK chatbot server. Please make sure the server is running on port 8003.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClearChat = () => {
    setMessages([
      {
        id: '1',
        role: 'assistant',
        content: '👋 Hi! I\'m your AI Marketing Assistant. How can I help you today?',
        timestamp: new Date(),
      },
    ]);
  };

  const quickPrompts = [
    'Show top performing campaigns',
    'What keywords are underperforming?',
    'Analyze my budget allocation',
    'Forecast next month\'s spend',
  ];

  return (
    <>
      {/* Side Panel Chat Window */}
      <Slide direction="left" in={isChatOpen} mountOnEnter unmountOnExit>
        <Paper
          elevation={8}
          sx={{
            position: 'fixed',
            top: 0,
            right: 0,
            width: `${chatPanelWidth}px`,
            height: '100vh',
            display: 'flex',
            flexDirection: 'column',
            borderRadius: 0,
            overflow: 'hidden',
            zIndex: 1300,
            bgcolor: 'background.paper',
            boxShadow: `-4px 0 24px ${alpha(theme.palette.primary.main, 0.2)}`,
            transition: 'width 0.1s ease-out',
          }}
        >
          {/* Resize Handle */}
          <Box
            ref={resizeHandleRef}
            onMouseDown={handleMouseDown}
            sx={{
              position: 'absolute',
              left: 0,
              top: 0,
              bottom: 0,
              width: '6px',
              cursor: 'col-resize',
              bgcolor: 'transparent',
              '&:hover': {
                bgcolor: alpha(theme.palette.primary.main, 0.1),
              },
              '&:active': {
                bgcolor: alpha(theme.palette.primary.main, 0.2),
              },
              zIndex: 1,
            }}
          />
          {/* Header */}
          <Box
            sx={{
              background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
              color: 'white',
              p: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <Avatar
                sx={{
                  bgcolor: alpha('#fff', 0.2),
                  width: 40,
                  height: 40,
                }}
              >
                <BotIcon />
              </Avatar>
              <Box>
                <Typography variant="subtitle1" fontWeight={600}>
                  AI Assistant
                </Typography>
                <Typography variant="caption" sx={{ opacity: 0.9 }}>
                  Powered by ADK Multi-Agent
                </Typography>
              </Box>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <IconButton
                size="small"
                onClick={handleClearChat}
                sx={{ color: 'white' }}
              >
                <RefreshIcon fontSize="small" />
              </IconButton>
              <IconButton
                size="small"
                onClick={() => setChatOpen(false)}
                sx={{ color: 'white' }}
              >
                <CloseIcon />
              </IconButton>
            </Box>
          </Box>

          {/* Quick Prompts */}
          {messages.length === 1 && (
            <Box
              sx={{
                p: 2,
                display: 'flex',
                flexWrap: 'wrap',
                gap: 1,
                borderBottom: `1px solid ${theme.palette.divider}`,
              }}
            >
              {quickPrompts.map((prompt, index) => (
                <Chip
                  key={index}
                  label={prompt}
                  size="small"
                  onClick={() => setInput(prompt)}
                  sx={{
                    cursor: 'pointer',
                    '&:hover': {
                      bgcolor: theme.palette.primary.main,
                      color: 'white',
                    },
                  }}
                />
              ))}
            </Box>
          )}

          {/* Messages */}
          <Box
            sx={{
              flexGrow: 1,
              overflowY: 'auto',
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              gap: 2,
              bgcolor: alpha(theme.palette.background.default, 0.5),
            }}
          >
            {messages.map((message) => (
              <Fade in key={message.id}>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: 1,
                    flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
                  }}
                >
                  <Avatar
                    sx={{
                      bgcolor:
                        message.role === 'user'
                          ? theme.palette.primary.main
                          : theme.palette.secondary.main,
                      width: 32,
                      height: 32,
                    }}
                  >
                    {message.role === 'user' ? (
                      <PersonIcon fontSize="small" />
                    ) : (
                      <BotIcon fontSize="small" />
                    )}
                  </Avatar>
                  <Paper
                    elevation={1}
                    sx={{
                      p: 1.5,
                      maxWidth: '75%',
                      borderRadius: 2,
                      bgcolor:
                        message.role === 'user'
                          ? theme.palette.primary.main
                          : theme.palette.background.paper,
                      color: message.role === 'user' ? 'white' : 'text.primary',
                    }}
                  >
                    {message.role === 'assistant' ? (
                      <ReactMarkdown
                        components={{
                          p: ({ children, ...props }: any) => (
                            <Typography variant="body2" sx={{ mb: 1, '&:last-child': { mb: 0 } }} {...props}>
                              {children}
                            </Typography>
                          ),
                          strong: ({ children, ...props }: any) => (
                            <Typography component="span" fontWeight={700} {...props}>
                              {children}
                            </Typography>
                          ),
                          ul: ({ children, ...props }: any) => (
                            <Box component="ul" sx={{ pl: 2, my: 1 }} {...props}>
                              {children}
                            </Box>
                          ),
                          li: ({ children, ...props }: any) => (
                            <Typography component="li" variant="body2" sx={{ mb: 0.5 }} {...props}>
                              {children}
                            </Typography>
                          ),
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>
                    ) : (
                      <Typography variant="body2">{message.content}</Typography>
                    )}
                    <Typography
                      variant="caption"
                      sx={{
                        display: 'block',
                        mt: 0.5,
                        opacity: 0.7,
                        fontSize: '0.7rem',
                      }}
                    >
                      {message.timestamp.toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </Typography>
                  </Paper>
                </Box>
              </Fade>
            ))}
            {loading && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Avatar
                  sx={{
                    bgcolor: theme.palette.secondary.main,
                    width: 32,
                    height: 32,
                  }}
                >
                  <BotIcon fontSize="small" />
                </Avatar>
                <Paper
                  elevation={1}
                  sx={{
                    p: 1.5,
                    borderRadius: 2,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                  }}
                >
                  <CircularProgress size={16} />
                  <Typography variant="body2" color="text.secondary">
                    Thinking...
                  </Typography>
                </Paper>
              </Box>
            )}
            <div ref={messagesEndRef} />
          </Box>

          {/* Input */}
          <Box
            sx={{
              p: 2,
              borderTop: `1px solid ${theme.palette.divider}`,
              bgcolor: 'background.paper',
            }}
          >
            <Box sx={{ display: 'flex', gap: 1 }}>
              <TextField
                fullWidth
                multiline
                maxRows={3}
                placeholder="Ask me anything about your campaigns..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={loading}
                size="small"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                  },
                }}
              />
              <IconButton
                color="primary"
                onClick={handleSend}
                disabled={!input.trim() || loading}
                sx={{
                  bgcolor: theme.palette.primary.main,
                  color: 'white',
                  '&:hover': {
                    bgcolor: theme.palette.primary.dark,
                  },
                  '&.Mui-disabled': {
                    bgcolor: theme.palette.action.disabledBackground,
                  },
                }}
              >
                <SendIcon />
              </IconButton>
            </Box>
          </Box>
        </Paper>
      </Slide>

      {/* Floating Button */}
      <Fab
        color="primary"
        onClick={() => setChatOpen(!isChatOpen)}
        sx={{
          position: 'fixed',
          bottom: 24,
          right: 24,
          zIndex: 1300,
          background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
          boxShadow: `0 4px 20px ${alpha(theme.palette.primary.main, 0.4)}`,
          '&:hover': {
            background: `linear-gradient(135deg, ${theme.palette.primary.dark} 0%, ${theme.palette.secondary.dark} 100%)`,
            transform: 'scale(1.1)',
          },
          transition: 'all 0.3s ease',
        }}
      >
        {isChatOpen ? <CloseIcon /> : <ChatIcon />}
      </Fab>
    </>
  );
};

export default FloatingChatbot;
