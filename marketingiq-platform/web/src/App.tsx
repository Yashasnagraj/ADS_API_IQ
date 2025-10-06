import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/common/Layout';

// Premium Landing Page
import { PremiumLandingPage } from './components/landing/PremiumLandingPage';

// Unified Dashboard
import UnifiedDashboard from './components/dashboard/UnifiedDashboard';

// import CampaignsDashboard from './agents/data_agent/CampaignsDashboard';
import CampaignsDashboard from './components/campaigns/EnhancedCampaignsDashboard';
import AdGroupsDashboard from './agents/data_agent/AdGroupsDashboard';
import KeywordsDashboard from './agents/data_agent/KeywordsDashboard';
import SearchTermsDashboard from './agents/data_agent/SearchTermsDashboard';
import MLFeaturesDashboard from './agents/data_agent/MLFeaturesDashboard';

import CampaignInsights from './agents/insight_agent/CampaignInsights';
import KeywordInsights from './agents/insight_agent/KeywordInsights';
import AnomalyDetection from './agents/insight_agent/AnomalyDetection';
import InsightsSummary from './agents/insight_agent/InsightsSummary';

import BudgetOptimizer from './agents/optimization_agent/BudgetOptimizer';
import KeywordOptimizer from './agents/optimization_agent/KeywordOptimizer';
import CampaignSimulator from './agents/optimization_agent/CampaignSimulator';

import CTRForecast from './agents/forecasting_agent/CTRForecast';
import SpendForecast from './agents/forecasting_agent/SpendForecast';
import ScenarioSimulator from './agents/forecasting_agent/ScenarioSimulator';

import ThresholdsMonitor from './agents/alert_agent/ThresholdsMonitor';
import AlertsDashboard from './agents/alert_agent/AlertsDashboard';

function App() {
  return (
    <Routes>
      {/* Landing Page - Full Screen (No Layout) */}
      <Route path="/" element={<PremiumLandingPage />} />
      <Route path="/landing" element={<PremiumLandingPage />} />

      {/* All Other Dashboards - With Layout */}
      <Route path="/*" element={
        <Layout>
          <Routes>
            <Route path="/dashboard" element={<UnifiedDashboard />} />

            <Route path="/data/campaigns" element={<CampaignsDashboard />} />
            <Route path="/data/adgroups" element={<AdGroupsDashboard />} />
            <Route path="/data/keywords" element={<KeywordsDashboard />} />
            <Route path="/data/search-terms" element={<SearchTermsDashboard />} />
            <Route path="/data/ml-features" element={<MLFeaturesDashboard />} />

            <Route path="/insights/campaigns" element={<CampaignInsights />} />
            <Route path="/insights/keywords" element={<KeywordInsights />} />
            <Route path="/insights/anomalies" element={<AnomalyDetection />} />
            <Route path="/insights/summary" element={<InsightsSummary />} />

            <Route path="/optimization/budget" element={<BudgetOptimizer />} />
            <Route path="/optimization/keywords" element={<KeywordOptimizer />} />
            <Route path="/optimization/simulator" element={<CampaignSimulator />} />

            <Route path="/forecasting/ctr" element={<CTRForecast />} />
            <Route path="/forecasting/spend" element={<SpendForecast />} />
            <Route path="/forecasting/scenarios" element={<ScenarioSimulator />} />

            <Route path="/alerts/thresholds" element={<ThresholdsMonitor />} />
            <Route path="/alerts/dashboard" element={<AlertsDashboard />} />
          </Routes>
        </Layout>
      } />
    </Routes>
  );
}

export default App;