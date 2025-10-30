/**
 * AI Intelligence API Client
 * Connects to backend AI endpoints
 */

import axios from 'axios';
import API_CONFIG from '../config/api';

// Use relative URL in development to go through webpack proxy
// In production, webpack will inject the actual API_BASE_URL
const baseURL = typeof API_CONFIG.BASE_URL === 'string' && API_CONFIG.BASE_URL.startsWith('http://localhost')
  ? '/api/v1/ai'  // Relative path for development (uses webpack proxy)
  : `${API_CONFIG.BASE_URL}/ai`;  // Full URL for production

const aiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ===== TYPES =====

export interface GreetingResponse {
  greeting: string;
  mood: 'positive' | 'neutral' | 'focused' | 'alert';
  message: string;
  call_to_action: string;
  metrics_summary: {
    total_campaigns: number;
    healthy_campaigns: number;
    roas: number;
    total_spend: number;
    total_revenue: number;
  };
  status: 'excellent' | 'good' | 'needs_attention' | 'critical' | 'no_data';
}

export interface UnifiedRecommendation {
  action_type: string;
  title: string;
  message: string;
  expected_outcome: string;
  confidence_score: number;
  priority: 'critical' | 'high' | 'medium' | 'low';
  supporting_data: any;
  actionable_steps: string[];
  generated_at: string;
}

export interface AnomalyAlert {
  metric_name: string;
  current_value: number;
  expected_range: [number, number];
  severity: 'critical' | 'warning' | 'info';
  message: string;
  affected_entity?: string;
  detected_at: string;
}

export interface ChatMessage {
  user_message: string;
  customer_id: number;
}

export interface ChatResponse {
  ai_response: string;
  data_backing?: any;
  suggested_actions: string[];
  related_insights: string[];
}

export interface DailyInsights {
  customer_id: number;
  date: string;
  greeting: GreetingResponse;
  top_recommendation: UnifiedRecommendation;
  insights: any[];
  anomaly_alerts: AnomalyAlert[];
  quick_stats: any;
}

// ===== API FUNCTIONS =====

/**
 * Get personalized greeting
 */
export const getGreeting = async (userName: string, customerId: number): Promise<GreetingResponse> => {
  const response = await aiClient.get('/greeting', {
    params: { user_name: userName, customer_id: customerId },
  });
  return response.data;
};

/**
 * Get unified AI recommendation
 */
export const getUnifiedRecommendation = async (customerId: number): Promise<UnifiedRecommendation> => {
  const response = await aiClient.get('/recommendation/unified', {
    params: { customer_id: customerId },
  });
  return response.data;
};

/**
 * Get anomaly alerts
 */
export const getAnomalies = async (customerId: number, date?: string) => {
  const response = await aiClient.get('/anomalies', {
    params: { customer_id: customerId, date },
  });
  return response.data;
};

/**
 * Get daily insights package
 */
export const getDailyInsights = async (userName: string, customerId: number): Promise<DailyInsights> => {
  const response = await aiClient.get('/insights/daily', {
    params: { user_name: userName, customer_id: customerId },
  });
  return response.data;
};

/**
 * Send chat message to AI
 */
export const sendChatMessage = async (message: ChatMessage): Promise<ChatResponse> => {
  const response = await aiClient.post('/chat', message);
  return response.data;
};

/**
 * Get PIE incrementality predictions
 */
export const getIncrementality = async (customerId: number, campaignId?: string) => {
  const response = await aiClient.get('/incrementality', {
    params: { customer_id: customerId, campaign_id: campaignId },
  });
  return response.data;
};

/**
 * Get Shapley attribution analysis
 */
export const getAttribution = async (customerId: number, daysLookback: number = 30) => {
  const response = await aiClient.get('/attribution', {
    params: { customer_id: customerId, days_lookback: daysLookback },
  });
  return response.data;
};

/**
 * Get LTV predictions and segments
 */
export const getLTVPredictions = async (customerId: number) => {
  const response = await aiClient.get('/ltv/predict', {
    params: { customer_id: customerId },
  });
  return response.data;
};

/**
 * Get AI system status
 */
export const getAIStatus = async (customerId: number) => {
  const response = await aiClient.get('/status', {
    params: { customer_id: customerId },
  });
  return response.data;
};

export default {
  getGreeting,
  getUnifiedRecommendation,
  getAnomalies,
  getDailyInsights,
  sendChatMessage,
  getIncrementality,
  getAttribution,
  getLTVPredictions,
  getAIStatus,
};
