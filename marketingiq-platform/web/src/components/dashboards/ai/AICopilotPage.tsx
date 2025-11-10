import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  Paper,
  IconButton,
  Chip,
  Stack,
  Avatar,
  Divider,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import CampaignIcon from '@mui/icons-material/Campaign';
import { useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { AIBadge, AILoadingState } from '../../ai/shared';
import { useFilters } from '../../../context/FilterContext';
import { colors } from '../../../theme/designTokens';
import { useSnackbar } from 'notistack';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/ai';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  chart_data?: any;
  actions?: { label: string; path: string }[];
  timestamp: Date;
}

export const AICopilotPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestedQueries, setSuggestedQueries] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { filters } = useFilters();
  const { enqueueSnackbar } = useSnackbar();
  const navigate = useNavigate();

  useEffect(() => {
    // Send welcome message
    if (messages.length === 0 && filters.customerId) {
      sendMessage('');
    }
  }, [filters.customerId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async (userMessage: string) => {
    if (!filters.customerId) {
      enqueueSnackbar('Please select a customer first', { variant: 'warning' });
      return;
    }

    // Add user message to chat
    if (userMessage.trim()) {
      const userMsg: Message = {
        id: Date.now().toString(),
        role: 'user',
        content: userMessage,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMsg]);
    }

    setLoading(true);
    setInputValue('');

    try {
      const response = await axios.post(`${API_BASE}/chat`, {
        message: userMessage,
        context: {
          customer_id: filters.customerId,
          date_range: {
            start: filters.dateRange.startDate,
            end: filters.dateRange.endDate,
          },
          current_page: window.location.pathname,
        },
      });

      // Check if response data is valid
      if (!response.data || !response.data.response) {
        throw new Error('Invalid response from AI Copilot');
      }

      // Add assistant response
      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.response,
        chart_data: response.data.chart_data,
        actions: response.data.actions,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMsg]);

      // Update suggested queries if provided
      if (response.data.suggested_queries) {
        setSuggestedQueries(response.data.suggested_queries);
      }
    } catch (error: any) {
      console.error('Error sending message:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to get response from AI Copilot';
      enqueueSnackbar(errorMessage, { variant: 'error' });

      // Add error message to chat
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `I encountered an error: ${errorMessage}. Please try again or rephrase your question.`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleSendClick = () => {
    if (inputValue.trim()) {
      sendMessage(inputValue);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendClick();
    }
  };

  const handleSuggestedQuery = (query: string) => {
    setInputValue(query);
    sendMessage(query);
  };

  const handleActionClick = (path: string) => {
    navigate(path);
  };

  return (
    <Box sx={{ p: 3, height: 'calc(100vh - 100px)', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 600, mb: 1 }}>
            AI Copilot
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Ask questions about your marketing performance in natural language
          </Typography>
        </Box>
        <AIBadge />
      </Box>

      {/* Chat Container */}
      <Paper
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          background: `linear-gradient(to bottom, ${colors.background.default}, ${colors.primary[50]})`,
        }}
      >
        {/* Messages Area */}
        <Box
          sx={{
            flex: 1,
            overflowY: 'auto',
            p: 3,
            display: 'flex',
            flexDirection: 'column',
            gap: 2,
          }}
        >
          {messages.length === 0 && !loading && (
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <SmartToyIcon sx={{ fontSize: 80, color: colors.primary.main, mb: 2 }} />
              <Typography variant="h5" sx={{ mb: 2 }}>
                Welcome to AI Copilot
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
                {filters.customerId
                  ? 'Ask me anything about your marketing performance, campaigns, keywords, or budget.'
                  : 'Please select a customer to start chatting.'}
              </Typography>

              {suggestedQueries.length > 0 && (
                <Box>
                  <Typography variant="subtitle2" sx={{ mb: 2 }}>
                    Try asking:
                  </Typography>
                  <Stack direction="column" spacing={1} alignItems="center">
                    {suggestedQueries.map((query, index) => (
                      <Chip
                        key={index}
                        label={query}
                        onClick={() => handleSuggestedQuery(query)}
                        sx={{ cursor: 'pointer', maxWidth: 400 }}
                      />
                    ))}
                  </Stack>
                </Box>
              )}
            </Box>
          )}

          {messages.map((message) => (
            <Box
              key={message.id}
              sx={{
                display: 'flex',
                gap: 2,
                alignItems: 'flex-start',
                flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
              }}
            >
              <Avatar
                sx={{
                  bgcolor: message.role === 'user' ? colors.primary.main : colors.ai.secondary,
                  width: 40,
                  height: 40,
                }}
              >
                {message.role === 'user' ? <PersonIcon /> : <SmartToyIcon />}
              </Avatar>

              <Box sx={{ flex: 1, maxWidth: '70%' }}>
                <Paper
                  sx={{
                    p: 2,
                    bgcolor: message.role === 'user' ? colors.primary[50] : 'background.paper',
                    border: message.role === 'assistant' ? `1px solid ${colors.primary.main}` : 'none',
                  }}
                >
                  <Box sx={{ '& p': { mb: 1 }, '& p:last-child': { mb: 0 } }}>
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                  </Box>

                  {/* Chart Data */}
                  {message.chart_data && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" sx={{ mb: 2 }}>
                        {message.chart_data.title}
                      </Typography>
                      <ResponsiveContainer width="100%" height={250}>
                        <LineChart data={message.chart_data.data}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" />
                          <YAxis />
                          <Tooltip />
                          <Legend />
                          {message.chart_data.type === 'line' && (
                            <Line
                              type="monotone"
                              dataKey="cpc"
                              stroke={colors.primary.main}
                              strokeWidth={2}
                              name="CPC (₹)"
                            />
                          )}
                        </LineChart>
                      </ResponsiveContainer>
                    </Box>
                  )}

                  {/* Action Buttons */}
                  {message.actions && message.actions.length > 0 && (
                    <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      {message.actions.map((action, index) => (
                        <Button
                          key={index}
                          size="small"
                          variant="outlined"
                          onClick={() => handleActionClick(action.path)}
                          startIcon={action.label.includes('Campaign') ? <CampaignIcon /> : <TrendingUpIcon />}
                        >
                          {action.label}
                        </Button>
                      ))}
                    </Box>
                  )}
                </Paper>

                <Typography variant="caption" color="text.secondary" sx={{ ml: 1, mt: 0.5, display: 'block' }}>
                  {message.timestamp.toLocaleTimeString()}
                </Typography>
              </Box>
            </Box>
          ))}

          {loading && (
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
              <Avatar sx={{ bgcolor: colors.ai.secondary, width: 40, height: 40 }}>
                <SmartToyIcon />
              </Avatar>
              <Box sx={{ flex: 1, maxWidth: '70%' }}>
                <AILoadingState message="AI is thinking..." size="small" variant="dots" />
              </Box>
            </Box>
          )}

          <div ref={messagesEndRef} />
        </Box>

        <Divider />

        {/* Input Area */}
        <Box sx={{ p: 2, bgcolor: 'background.paper' }}>
          {/* Suggested Queries */}
          {suggestedQueries.length > 0 && messages.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                Suggested questions:
              </Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap">
                {suggestedQueries.slice(0, 3).map((query, index) => (
                  <Chip
                    key={index}
                    label={query}
                    size="small"
                    onClick={() => handleSuggestedQuery(query)}
                    sx={{ cursor: 'pointer', mb: 1 }}
                  />
                ))}
              </Stack>
            </Box>
          )}

          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              placeholder="Ask me anything... e.g., 'Why is my CPC increasing?'"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={loading || !filters.customerId}
              sx={{
                '& .MuiOutlinedInput-root': {
                  bgcolor: 'background.default',
                },
              }}
            />
            <Button
              variant="contained"
              onClick={handleSendClick}
              disabled={loading || !inputValue.trim() || !filters.customerId}
              sx={{ minWidth: 60, height: 56 }}
            >
              <SendIcon />
            </Button>
          </Box>

          {!filters.customerId && (
            <Typography variant="caption" color="error" sx={{ mt: 1, display: 'block' }}>
              Please select a customer to start chatting
            </Typography>
          )}
        </Box>
      </Paper>
    </Box>
  );
};

export default AICopilotPage;
