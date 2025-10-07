/**
 * API Configuration
 * Centralized configuration for API endpoints
 * Supports environment variables for production deployment
 */

// Check if we're in production (Netlify sets NODE_ENV to 'production')
const isProduction = process.env.NODE_ENV === 'production';

// Get API URLs from environment variables or use defaults
const getApiUrl = (envVar: string, defaultUrl: string) => {
  // In browser, check for runtime env vars (set via Netlify UI)
  if (typeof window !== 'undefined' && (window as any).ENV) {
    return (window as any).ENV[envVar] || defaultUrl;
  }
  // In build time, use process.env
  return process.env[envVar] || defaultUrl;
};

export const API_CONFIG = {
  // Backend REST API (SQLite)
  // Set REACT_APP_API_URL in Netlify environment variables
  BASE_URL: getApiUrl(
    'REACT_APP_API_URL',
    isProduction
      ? 'https://your-backend-api.com/api/v1'  // Replace with your actual backend URL
      : 'http://localhost:8000/api/v1'
  ),

  // Main Data API (SQLite-based)
  DATA_API_URL: getApiUrl(
    'REACT_APP_DATA_API_URL',
    isProduction
      ? 'https://your-backend-api.com'
      : 'http://localhost:8000'
  ),

  // Multi-Agent System API
  AGENT_API_URL: getApiUrl(
    'REACT_APP_AGENT_API_URL',
    isProduction
      ? 'https://your-agent-api.com/api'
      : 'http://localhost:8001/api'
  ),

  // ADK Chatbot API
  CHATBOT_API_URL: getApiUrl(
    'REACT_APP_CHATBOT_API_URL',
    isProduction
      ? 'https://your-chatbot-api.com/api'
      : 'http://localhost:8002/api'
  ),

  // Request timeout (ms)
  TIMEOUT: 30000,

  // Enable debug logging (disabled in production)
  DEBUG: !isProduction,
} as const;

export default API_CONFIG;