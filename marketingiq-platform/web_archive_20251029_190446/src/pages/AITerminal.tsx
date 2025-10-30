/**
 * AI Terminal Command Center
 * Main intelligence dashboard with terminal aesthetic
 */

import React, { useState, useEffect, useRef } from 'react';
import aiApi, { GreetingResponse, UnifiedRecommendation, ChatResponse } from '../services/ai-api';
import '../styles/terminal.css';

const AITerminal: React.FC = () => {
  const [greeting, setGreeting] = useState<GreetingResponse | null>(null);
  const [recommendation, setRecommendation] = useState<UnifiedRecommendation | null>(null);
  const [chatMessages, setChatMessages] = useState<Array<{ type: 'user' | 'ai'; message: string }>>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date().toLocaleTimeString());
  const chatEndRef = useRef<HTMLDivElement>(null);

  const customerId = 5032737756; // Emcee Sons
  const userName = 'Yashas';

  // Update time every second
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Load initial data
  useEffect(() => {
    loadAIData();
  }, []);

  // Auto-scroll chat to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const loadAIData = async () => {
    try {
      setIsLoading(true);
      const [greetingData, recommendationData] = await Promise.all([
        aiApi.getGreeting(userName, customerId),
        aiApi.getUnifiedRecommendation(customerId),
      ]);
      setGreeting(greetingData);
      setRecommendation(recommendationData);
    } catch (error) {
      console.error('Error loading AI data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    // Add user message to chat
    const userMessage = inputMessage.trim();
    setChatMessages(prev => [...prev, { type: 'user', message: userMessage }]);
    setInputMessage('');

    try {
      // Send to AI
      const response = await aiApi.sendChatMessage({
        user_message: userMessage,
        customer_id: customerId,
      });

      // Add AI response
      setChatMessages(prev => [...prev, { type: 'ai', message: response.ai_response }]);
    } catch (error) {
      console.error('Error sending chat message:', error);
      setChatMessages(prev => [...prev, {
        type: 'ai',
        message: 'Error processing your request. Please try again.',
      }]);
    }
  };

  const getMoodEmoji = (mood?: string) => {
    switch (mood) {
      case 'positive': return '☀️';
      case 'focused': return '💼';
      case 'alert': return '🚨';
      default: return '👋';
    }
  };

  const getPriorityIcon = (priority?: string) => {
    switch (priority) {
      case 'critical': return '🚨';
      case 'high': return '💡';
      case 'medium': return '📊';
      default: return 'ℹ️';
    }
  };

  return (
    <div className="terminal-container">
      {/* TERMINAL HEADER */}
      <div className="terminal-header">
        <div className="terminal-header-line">
          MARKETINGIQ INTELLIGENCE TERMINAL v2.0
        </div>
        <div className="terminal-header-line">
          LOGGED IN: {userName.toLowerCase()}@emcee-sons
          <span className="terminal-status operational"> | STATUS: OPERATIONAL</span>
          <span className="terminal-status"> | TIME: {currentTime}</span>
        </div>
        <div className="terminal-header-line">
          CUSTOMER: {customerId} | MODE: AI-FIRST
        </div>
      </div>

      {/* AI GREETING */}
      {greeting && (
        <div className="mb-3">
          <div className="terminal-text opacity-70" style={{ fontSize: '12px' }}>
            [{new Date().toLocaleTimeString()}] AI:
          </div>
          <div className="terminal-text-secondary" style={{ fontSize: '16px', marginLeft: '16px' }}>
            {greeting.greeting} {getMoodEmoji(greeting.mood)}
          </div>
          <div className="terminal-text-secondary" style={{ marginLeft: '16px' }}>
            {greeting.message}
          </div>
          {greeting.metrics_summary.total_campaigns > 0 && (
            <div className="terminal-text opacity-70" style={{ fontSize: '12px', marginLeft: '16px', marginTop: '8px' }}>
              STATUS: {greeting.metrics_summary.total_campaigns} campaigns active |
              ₹{greeting.metrics_summary.total_spend.toLocaleString()} spend |
              {greeting.metrics_summary.roas.toFixed(2)}x ROAS
            </div>
          )}
        </div>
      )}

      {/* PRIORITY INSIGHT CARD */}
      {recommendation && (
        <div className="insight-card">
          <div className="insight-card-title">
            <span className="insight-card-icon">{getPriorityIcon(recommendation.priority)}</span>
            {recommendation.title.replace(/[🚨💡📋⚠️📊📈ℹ️]/g, '').trim()}
          </div>

          <div className="insight-card-message">
            {recommendation.message}
          </div>

          <div className="insight-card-stats">
            <div className="insight-stat">
              <div className="insight-stat-label">Expected Outcome</div>
              <div className="insight-stat-value">{recommendation.expected_outcome}</div>
            </div>
            <div className="insight-stat">
              <div className="insight-stat-label">Confidence</div>
              <div className="insight-stat-value">{(recommendation.confidence_score * 100).toFixed(0)}%</div>
            </div>
            <div className="insight-stat">
              <div className="insight-stat-label">Priority</div>
              <div className="insight-stat-value">{recommendation.priority.toUpperCase()}</div>
            </div>
          </div>

          {recommendation.actionable_steps && recommendation.actionable_steps.length > 0 && (
            <div style={{ marginTop: '16px' }}>
              <div className="terminal-text" style={{ fontSize: '12px', marginBottom: '8px' }}>
                ACTIONABLE STEPS:
              </div>
              {recommendation.actionable_steps.map((step, idx) => (
                <div key={idx} className="terminal-text-secondary" style={{ fontSize: '12px', marginLeft: '16px', marginBottom: '4px' }}>
                  {idx + 1}. {step}
                </div>
              ))}
            </div>
          )}

          <div style={{ marginTop: '16px', display: 'flex', gap: '8px' }}>
            <button className="terminal-button-accent" onClick={() => alert('Execute recommendation')}>
              APPLY
            </button>
            <button className="terminal-button" onClick={() => alert('Show details')}>
              DETAILS
            </button>
            <button className="terminal-button" onClick={() => setRecommendation(null)}>
              DISMISS
            </button>
          </div>
        </div>
      )}

      {/* CHAT INTERFACE */}
      <div className="terminal-card">
        <div className="terminal-card-title">COMMAND INPUT</div>

        <div className="chat-container">
          {chatMessages.length === 0 && (
            <div className="terminal-text opacity-50" style={{ fontSize: '12px', textAlign: 'center', padding: '20px' }}>
              Ask me anything about your marketing performance...
            </div>
          )}

          {chatMessages.map((msg, idx) => (
            <div key={idx} className={`chat-message chat-message-${msg.type}`}>
              {msg.message}
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>

        <form onSubmit={handleSendMessage} className="chat-input-container">
          <input
            type="text"
            className="chat-input"
            placeholder="yashas@emcee: _"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            disabled={isLoading}
          />
          <button
            type="submit"
            className="terminal-button-accent"
            disabled={isLoading || !inputMessage.trim()}
          >
            SEND
          </button>
        </form>
      </div>

      {/* QUICK COMMANDS */}
      <div className="mt-3">
        <div className="terminal-text opacity-70" style={{ fontSize: '12px', marginBottom: '8px' }}>
          QUICK COMMANDS:
        </div>
        <div className="quick-commands">
          <button className="quick-command" onClick={() => alert('Show campaigns dashboard')}>
            show campaigns
          </button>
          <button className="quick-command" onClick={() => alert('Show attribution analysis')}>
            attribution
          </button>
          <button className="quick-command" onClick={() => alert('Show LTV segments')}>
            ltv-segments
          </button>
          <button className="quick-command" onClick={() => alert('Show incrementality predictions')}>
            incrementality
          </button>
          <button className="quick-command" onClick={loadAIData}>
            refresh
          </button>
          <button className="quick-command" onClick={() => alert('Help commands:\n- show campaigns\n- attribution\n- ltv-segments\n- incrementality\n- refresh')}>
            help
          </button>
        </div>
      </div>

      {/* FOOTER STATUS */}
      <div className="mt-4" style={{ borderTop: '1px solid rgba(0, 255, 159, 0.2)', paddingTop: '16px' }}>
        <div className="terminal-text opacity-50" style={{ fontSize: '11px', textAlign: 'center' }}>
          MARKETINGIQ AI INTELLIGENCE | POWERED BY CLAUDE | {new Date().toLocaleDateString()}
        </div>
      </div>
    </div>
  );
};

export default AITerminal;
