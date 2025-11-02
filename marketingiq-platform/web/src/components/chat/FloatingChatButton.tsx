// Floating Chat Button - AI Assistant powered by Google ADK Multi-Agent System
import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Fab,
  Paper,
  TextField,
  Typography,
  IconButton,
  Stack,
  Avatar,
  Chip,
  CircularProgress,
  Fade,
  Tooltip,
} from '@mui/material';
import {
  Chat as ChatIcon,
  Close as CloseIcon,
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  Analytics as AnalyticsIcon,
  AutoAwesome as SparklesIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useFilters } from '../../context/FilterContext';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

// Chat message interface
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  metadata?: any;
}

// Chat API base URL
const CHAT_API_URL = 'http://localhost:8003/api/chat';

export const FloatingChatButton: React.FC = () => {
  const { filters } = useFilters();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      role: 'assistant',
      content: `👋 Hi! I'm your **AI Marketing Assistant** powered by Google ADK's multi-agent system.

Ask me anything about your campaigns:
• **Campaign Performance**: "Show me top performing campaigns"
• **Keyword Analysis**: "Which keywords are underperforming?"
• **Budget Optimization**: "How should I allocate my budget?"
• **Forecasting**: "Predict next month's performance"
• **Anomaly Detection**: "Are there any issues in my campaigns?"

What would you like to know?`,
      timestamp: new Date(),
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Call ADK Chatbot API
      const response = await axios.post(CHAT_API_URL, {
        message: inputMessage,
        customer_id: filters.customerId ? String(filters.customerId) : undefined,
        campaign_type: filters.campaignType,
        date_range: filters.dateRange,
        context: {
          current_page: window.location.pathname,
        },
      });

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date(response.data.timestamp),
        metadata: response.data.metadata,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      console.error('Chat API error:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `⚠️ Sorry, I couldn't process that request. ${
          error.response?.data?.detail || error.message || 'Please make sure the ADK chatbot server is running on port 8003.'
        }`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <>
      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            style={{
              position: 'fixed',
              bottom: 100,
              right: 24,
              zIndex: 1300,
            }}
          >
            <Paper
              elevation={8}
              sx={{
                width: { xs: 'calc(100vw - 48px)', sm: 400 },
                height: 600,
                display: 'flex',
                flexDirection: 'column',
                borderRadius: 3,
                overflow: 'hidden',
                boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
              }}
            >
              {/* Header */}
              <Box
                sx={{
                  p: 2,
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}
              >
                <Stack direction="row" spacing={1.5} alignItems="center">
                  <Avatar
                    sx={{
                      bgcolor: 'rgba(255,255,255,0.25)',
                      width: 40,
                      height: 40,
                      border: '2px solid rgba(255,255,255,0.3)',
                    }}
                  >
                    <AnalyticsIcon sx={{ fontSize: 24 }} />
                  </Avatar>
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '1rem', display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      AI Marketing Assistant
                      <SparklesIcon sx={{ fontSize: 16 }} />
                    </Typography>
                    <Typography variant="caption" sx={{ opacity: 0.9 }}>
                      Powered by Google ADK + Gemini
                    </Typography>
                  </Box>
                </Stack>
                <IconButton
                  size="small"
                  onClick={() => setIsOpen(false)}
                  sx={{ color: 'white' }}
                >
                  <CloseIcon />
                </IconButton>
              </Box>

              {/* Messages Container */}
              <Box
                ref={chatContainerRef}
                sx={{
                  flex: 1,
                  overflowY: 'auto',
                  p: 2,
                  bgcolor: '#f5f5f5',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 2,
                }}
              >
                {messages.map((msg) => (
                  <Box
                    key={msg.id}
                    sx={{
                      display: 'flex',
                      flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
                      gap: 1,
                    }}
                  >
                    <Avatar
                      sx={{
                        bgcolor: msg.role === 'user' ? 'primary.main' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        width: 32,
                        height: 32,
                        border: msg.role === 'assistant' ? '2px solid rgba(102, 126, 234, 0.3)' : 'none',
                      }}
                    >
                      {msg.role === 'user' ? <PersonIcon sx={{ fontSize: 20 }} /> : <AnalyticsIcon sx={{ fontSize: 20 }} />}
                    </Avatar>
                    <Paper
                      elevation={1}
                      sx={{
                        p: 1.5,
                        maxWidth: '75%',
                        bgcolor: msg.role === 'user' ? 'primary.main' : 'white',
                        color: msg.role === 'user' ? 'white' : 'text.primary',
                        borderRadius: 2,
                        '& p': { m: 0 },
                        '& ul, & ol': { mt: 1, mb: 1, pl: 2 },
                        '& strong': { fontWeight: 600 },
                        '& code': {
                          bgcolor: msg.role === 'user' ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.05)',
                          p: 0.5,
                          borderRadius: 0.5,
                          fontSize: '0.875rem',
                        },
                      }}
                    >
                      {msg.role === 'assistant' ? (
                        <Box
                          sx={{
                            '& p': { m: 0, mb: 1, lineHeight: 1.6 },
                            '& p:last-child': { mb: 0 },
                            '& ul, & ol': { mt: 0.5, mb: 0.5, pl: 2.5 },
                            '& li': { mb: 0.5 },
                            '& strong': { fontWeight: 700, color: msg.role === 'assistant' ? 'text.primary' : 'inherit' },
                            '& em': { fontStyle: 'italic', opacity: 0.9 },
                            '& code': {
                              bgcolor: msg.role === 'user' ? 'rgba(255,255,255,0.2)' : 'rgba(102, 126, 234, 0.1)',
                              color: msg.role === 'user' ? 'white' : '#667eea',
                              p: 0.5,
                              px: 0.75,
                              borderRadius: 0.5,
                              fontSize: '0.875rem',
                              fontFamily: 'monospace',
                            },
                            '& h1, & h2, & h3, & h4, & h5, & h6': {
                              mt: 1,
                              mb: 0.5,
                              fontWeight: 600,
                            },
                            '& blockquote': {
                              borderLeft: '3px solid rgba(102, 126, 234, 0.3)',
                              pl: 1.5,
                              ml: 0,
                              my: 1,
                              fontStyle: 'italic',
                              opacity: 0.9,
                            },
                          }}
                        >
                          <ReactMarkdown>{msg.content}</ReactMarkdown>
                        </Box>
                      ) : (
                        <Typography
                          variant="body2"
                          sx={{
                            whiteSpace: 'pre-wrap',
                            wordBreak: 'break-word',
                            lineHeight: 1.6,
                          }}
                        >
                          {msg.content}
                        </Typography>
                      )}
                      {msg.metadata?.agent_used && (
                        <Chip
                          label={`Agent: ${msg.metadata.agent_used}`}
                          size="small"
                          sx={{ mt: 1, height: 20, fontSize: '0.7rem' }}
                        />
                      )}
                    </Paper>
                  </Box>
                ))}

                {isLoading && (
                  <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                    <Avatar
                      sx={{
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        width: 32,
                        height: 32,
                        border: '2px solid rgba(102, 126, 234, 0.3)',
                      }}
                    >
                      <AnalyticsIcon sx={{ fontSize: 20 }} />
                    </Avatar>
                    <Paper
                      elevation={1}
                      sx={{
                        p: 1.5,
                        borderRadius: 2,
                        display: 'flex',
                        gap: 1,
                        alignItems: 'center',
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

              {/* Input Area */}
              <Box
                sx={{
                  p: 2,
                  borderTop: '1px solid',
                  borderColor: 'divider',
                  bgcolor: 'white',
                }}
              >
                <Stack direction="row" spacing={1}>
                  <TextField
                    fullWidth
                    size="small"
                    placeholder="Ask me anything about your campaigns..."
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    disabled={isLoading}
                    multiline
                    maxRows={3}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        borderRadius: 2,
                      },
                    }}
                  />
                  <IconButton
                    color="primary"
                    onClick={handleSendMessage}
                    disabled={!inputMessage.trim() || isLoading}
                    sx={{
                      bgcolor: 'primary.main',
                      color: 'white',
                      '&:hover': {
                        bgcolor: 'primary.dark',
                      },
                      '&:disabled': {
                        bgcolor: 'action.disabledBackground',
                      },
                    }}
                  >
                    <SendIcon />
                  </IconButton>
                </Stack>
              </Box>
            </Paper>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Floating Action Button */}
      <Tooltip title="AI Assistant" placement="left">
        <Fab
          color="primary"
          onClick={() => setIsOpen(!isOpen)}
          sx={{
            position: 'fixed',
            bottom: 24,
            right: 24,
            zIndex: 1300,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            '&:hover': {
              background: 'linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%)',
              transform: 'scale(1.05)',
            },
            transition: 'all 0.3s ease',
            boxShadow: '0 4px 20px rgba(102, 126, 234, 0.4)',
          }}
        >
          <motion.div
            animate={isOpen ? { rotate: 90 } : { rotate: 0 }}
            transition={{ duration: 0.3 }}
          >
            {isOpen ? <CloseIcon /> : <ChatIcon />}
          </motion.div>
        </Fab>
      </Tooltip>
    </>
  );
};
