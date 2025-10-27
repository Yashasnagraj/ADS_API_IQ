/**
 * API Configuration
 * Centralized configuration for API endpoints
 * Supports environment variables for production deployment
 */

// @ts-ignore - Webpack DefinePlugin will replace these at build time
declare const REACT_APP_API_URL: string | undefined;
// @ts-ignore
declare const REACT_APP_DATA_API_URL: string | undefined;
// @ts-ignore
declare const REACT_APP_AGENT_API_URL: string | undefined;
// @ts-ignore
declare const REACT_APP_CHATBOT_API_URL: string | undefined;
// @ts-ignore
declare const NODE_ENV: string | undefined;

// Check if we're in production (webpack DefinePlugin injects this)
const isProduction = typeof NODE_ENV !== 'undefined' && NODE_ENV === 'production';

// Helper to get env var with fallback
const getEnvVar = (value: string | undefined, fallback: string): string => {
  return value || fallback;
};

export const API_CONFIG = {
  // Backend REST API (SQLite)
  // Set REACT_APP_API_URL in Netlify environment variables
  BASE_URL: getEnvVar(
    typeof REACT_APP_API_URL !== 'undefined' ? REACT_APP_API_URL : undefined,
    isProduction
      ? 'https://your-backend-api.com/api/v1'  // Replace with your actual backend URL
      : 'http://localhost:8000/api/v1'
  ),

  // Main Data API (SQLite-based)
  DATA_API_URL: getEnvVar(
    typeof REACT_APP_DATA_API_URL !== 'undefined' ? REACT_APP_DATA_API_URL : undefined,
    isProduction
      ? 'https://your-backend-api.com'
      : 'http://localhost:8000'
  ),

  // Multi-Agent System API
  AGENT_API_URL: getEnvVar(
    typeof REACT_APP_AGENT_API_URL !== 'undefined' ? REACT_APP_AGENT_API_URL : undefined,
    isProduction
      ? 'https://your-agent-api.com/api'
      : 'http://localhost:8000/api'
  ),

  // ADK Chatbot API
  CHATBOT_API_URL: getEnvVar(
    typeof REACT_APP_CHATBOT_API_URL !== 'undefined' ? REACT_APP_CHATBOT_API_URL : undefined,
    isProduction
      ? 'https://your-chatbot-api.com/api'
      : 'http://localhost:8003/api'
  ),

  // Request timeout (ms)
  TIMEOUT: 30000,

  // Enable debug logging (disabled in production)
  DEBUG: !isProduction,
} as const;

export default API_CONFIG;