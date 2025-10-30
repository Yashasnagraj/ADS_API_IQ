// Main App Component with Routing
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { theme } from './theme';
import { FilterProvider } from './context/FilterContext';
import { Layout } from './components/common/Layout';
import { LandingPage } from './components/landing/LandingPage';

// Platform Dashboards
import { UnifiedDashboard } from './components/dashboard/UnifiedDashboard';
import { GoogleAdsDashboard } from './components/dashboard/GoogleAdsDashboard';
import { MetaAdsDashboard } from './components/dashboard/MetaAdsDashboard';
import { GA4Dashboard } from './components/dashboard/GA4Dashboard';
import { EcommerceDashboard } from './components/dashboard/EcommerceDashboard';

// Data Agent Dashboards
import CampaignsDashboard from './components/dashboards/agents/data_agent/CampaignsDashboard';
import KeywordsDashboard from './components/dashboards/agents/data_agent/KeywordsDashboard';
import AdGroupsDashboard from './components/dashboards/agents/data_agent/AdGroupsDashboard';
import SearchTermsDashboard from './components/dashboards/agents/data_agent/SearchTermsDashboard';
import MLFeaturesDashboard from './components/dashboards/agents/data_agent/MLFeaturesDashboard';
import EnrichedCampaignsDashboard from './components/dashboards/agents/data_agent/EnrichedCampaignsDashboard';

// Insight Agent Dashboards
import CampaignInsights from './components/dashboards/agents/insight_agent/CampaignInsights';
import KeywordInsights from './components/dashboards/agents/insight_agent/KeywordInsights';
import AnomalyDetection from './components/dashboards/agents/insight_agent/AnomalyDetection';
import InsightsSummary from './components/dashboards/agents/insight_agent/InsightsSummary';

// Optimization Agent Dashboards
import BudgetOptimizer from './components/dashboards/agents/optimization_agent/BudgetOptimizer';
import KeywordOptimizer from './components/dashboards/agents/optimization_agent/KeywordOptimizer';
import CampaignSimulator from './components/dashboards/agents/optimization_agent/CampaignSimulator';

// Forecasting Agent Dashboards
import CTRForecast from './components/dashboards/agents/forecasting_agent/CTRForecast';
import SpendForecast from './components/dashboards/agents/forecasting_agent/SpendForecast';
import ScenarioSimulator from './components/dashboards/agents/forecasting_agent/ScenarioSimulator';

// Alert Agent Dashboards
import AlertsDashboard from './components/dashboards/agents/alert_agent/AlertsDashboard';
import ThresholdsMonitor from './components/dashboards/agents/alert_agent/ThresholdsMonitor';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <FilterProvider>
        <Router>
          <Routes>
            {/* Landing Page */}
            <Route path="/" element={<LandingPage />} />

            {/* Dashboards with Layout */}
            <Route
              path="/dashboard/*"
              element={
                <Layout>
                  <Routes>
                    {/* Default redirect */}
                    <Route index element={<Navigate to="/dashboard/unified" replace />} />

                    {/* Platform Dashboards */}
                    <Route path="unified" element={<UnifiedDashboard />} />
                    <Route path="google-ads" element={<GoogleAdsDashboard />} />
                    <Route path="meta-ads" element={<MetaAdsDashboard />} />
                    <Route path="ga4" element={<GA4Dashboard />} />
                    <Route path="ecommerce" element={<EcommerceDashboard />} />

                    {/* Data Agent Dashboards */}
                    <Route path="data/campaigns" element={<CampaignsDashboard />} />
                    <Route path="data/keywords" element={<KeywordsDashboard />} />
                    <Route path="data/adgroups" element={<AdGroupsDashboard />} />
                    <Route path="data/search-terms" element={<SearchTermsDashboard />} />
                    <Route path="data/ml-features" element={<MLFeaturesDashboard />} />
                    <Route path="data/enriched-campaigns" element={<EnrichedCampaignsDashboard />} />

                    {/* Insight Agent Dashboards */}
                    <Route path="insights/campaigns" element={<CampaignInsights />} />
                    <Route path="insights/keywords" element={<KeywordInsights />} />
                    <Route path="insights/anomalies" element={<AnomalyDetection />} />
                    <Route path="insights/summary" element={<InsightsSummary />} />

                    {/* Optimization Agent Dashboards */}
                    <Route path="optimization/budget" element={<BudgetOptimizer />} />
                    <Route path="optimization/keywords" element={<KeywordOptimizer />} />
                    <Route path="optimization/simulator" element={<CampaignSimulator />} />

                    {/* Forecasting Agent Dashboards */}
                    <Route path="forecasting/ctr" element={<CTRForecast />} />
                    <Route path="forecasting/spend" element={<SpendForecast />} />
                    <Route path="forecasting/scenarios" element={<ScenarioSimulator />} />

                    {/* Alert Agent Dashboards */}
                    <Route path="alerts/dashboard" element={<AlertsDashboard />} />
                    <Route path="alerts/thresholds" element={<ThresholdsMonitor />} />
                  </Routes>
                </Layout>
              }
            />

            {/* Redirect unknown routes to landing */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </FilterProvider>
    </ThemeProvider>
  );
}

export default App;
