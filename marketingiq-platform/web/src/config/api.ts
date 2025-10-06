/**
 * API Configuration
 * Centralized configuration for API endpoints
 */

export const API_CONFIG = {
  // Backend REST API (SQLite)
  BASE_URL: 'http://localhost:8000/api/v1',

  // Main Data API (SQLite-based)
  DATA_API_URL: 'http://localhost:8000',

  // Multi-Agent System API
  AGENT_API_URL: 'http://localhost:8001/api',

  // ADK Chatbot API
  CHATBOT_API_URL: 'http://localhost:8002/api',

  // Request timeout (ms)
  TIMEOUT: 30000,

  // Enable debug logging
  DEBUG: true,
} as const;

export default API_CONFIG;