import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Stepper,
  Step,
  StepLabel,
  Card,
  CardContent,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  FormControlLabel,
  FormGroup,
  Divider,
  Paper,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import DescriptionIcon from '@mui/icons-material/Description';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import EmailIcon from '@mui/icons-material/Email';
import ReactMarkdown from 'react-markdown';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { AIBadge, AILoadingState, GradientCard } from '../../ai/shared';
import { useFilters, getDateRangeValues } from '../../../context/FilterContext';
import { colors, shadows } from '../../../theme/designTokens';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/ai';

const reportTypes = [
  {
    id: 'executive',
    title: 'Executive Summary',
    description: 'Quick 5-min overview of key metrics',
    icon: <DescriptionIcon sx={{ fontSize: 48 }} />,
  },
  {
    id: 'client',
    title: 'Client Report',
    description: 'Branded PDF for client presentations',
    icon: <PictureAsPdfIcon sx={{ fontSize: 48 }} />,
  },
  {
    id: 'campaign',
    title: 'Campaign Postmortem',
    description: 'Deep dive analysis of specific campaigns',
    icon: <AnalyticsIcon sx={{ fontSize: 48 }} />,
  },
  {
    id: 'weekly',
    title: 'Weekly Digest',
    description: 'Automated weekly performance summary',
    icon: <CalendarMonthIcon sx={{ fontSize: 48 }} />,
  },
  {
    id: 'performance',
    title: 'Performance Review',
    description: 'Comprehensive monthly performance report',
    icon: <TrendingUpIcon sx={{ fontSize: 48 }} />,
  },
  {
    id: 'email',
    title: 'Email Newsletter',
    description: 'Email-friendly performance update',
    icon: <EmailIcon sx={{ fontSize: 48 }} />,
  },
];

const steps = ['Select Report Type', 'Configure Settings', 'Generate Report'];

export const AIReportsPage: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [selectedType, setSelectedType] = useState('');
  const [loading, setLoading] = useState(false);
  const [generatedReport, setGeneratedReport] = useState<any>(null);
  const { filters } = useFilters();

  // Initialize dates from global filter context
  const { startDate: globalStartDate, endDate: globalEndDate } = getDateRangeValues(filters);

  const [config, setConfig] = useState({
    reportName: '',
    startDate: globalStartDate,
    endDate: globalEndDate,
    campaigns: 'all',
    includeSections: {
      executiveSummary: true,
      performanceTrends: true,
      aiInsights: true,
      topCampaigns: true,
      improvements: true,
      budgetAnalysis: true,
    },
  });

  // Update config when global filters change
  useEffect(() => {
    const { startDate, endDate } = getDateRangeValues(filters);
    setConfig((prev) => ({
      ...prev,
      startDate,
      endDate,
    }));
  }, [filters.dateRange]);

  const handleNext = async () => {
    if (activeStep === steps.length - 2) {
      // Generate report
      await generateReport();
    }
    setActiveStep((prev) => prev + 1);
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
  };

  const generateReport = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/reports/generate`, {
        report_name: config.reportName || `${selectedType} Report`,
        report_type: selectedType,
        customer_id: filters.customerId,
        start_date: config.startDate.toISOString().split('T')[0],
        end_date: config.endDate.toISOString().split('T')[0],
        campaigns: config.campaigns,
        include_sections: config.includeSections,
        branding: {
          color_scheme: colors.primary.main,
        },
      });

      setGeneratedReport(response.data.report);
    } catch (error) {
      console.error('Error generating report:', error);
    } finally {
      setLoading(false);
    }
  };

  const downloadPDF = () => {
    // In production, this would generate a PDF
    alert('PDF download feature coming soon!');
  };

  const shareReport = () => {
    // In production, this would generate a shareable link
    alert('Share feature coming soon!');
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 600, mb: 1 }}>
            AI Reports Generator
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Generate comprehensive marketing reports with AI-powered insights
          </Typography>
        </Box>
        <AIBadge />
      </Box>

      {/* Stepper */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Stepper activeStep={activeStep}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {/* Step Content */}
      {activeStep === 0 && (
        <Box>
          <Typography variant="h6" sx={{ mb: 3 }}>
            Select Report Type
          </Typography>
          <Grid container spacing={3}>
            {reportTypes.map((type) => (
              <Grid item xs={12} md={4} key={type.id}>
                <Card
                  sx={{
                    cursor: 'pointer',
                    border: selectedType === type.id ? `2px solid ${colors.primary.main}` : '2px solid transparent',
                    transition: 'all 0.3s',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: shadows.lg,
                    },
                  }}
                  onClick={() => setSelectedType(type.id)}
                >
                  <CardContent sx={{ textAlign: 'center', py: 4 }}>
                    <Box sx={{ color: colors.primary.main, mb: 2 }}>{type.icon}</Box>
                    <Typography variant="h6" sx={{ mb: 1 }}>
                      {type.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {type.description}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {activeStep === 1 && (
        <Box>
          <Typography variant="h6" sx={{ mb: 3 }}>
            Configure Report Settings
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Report Name"
                value={config.reportName}
                onChange={(e) => setConfig({ ...config, reportName: e.target.value })}
                placeholder={`My ${selectedType} Report`}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DatePicker
                  label="Start Date"
                  value={config.startDate}
                  onChange={(date) => date && setConfig({ ...config, startDate: date })}
                  slotProps={{ textField: { fullWidth: true } }}
                />
              </LocalizationProvider>
            </Grid>

            <Grid item xs={12} md={6}>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DatePicker
                  label="End Date"
                  value={config.endDate}
                  onChange={(date) => date && setConfig({ ...config, endDate: date })}
                  slotProps={{ textField: { fullWidth: true } }}
                />
              </LocalizationProvider>
            </Grid>

            <Grid item xs={12}>
              <Typography variant="subtitle1" sx={{ mb: 2 }}>
                Include Sections:
              </Typography>
              <FormGroup>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={config.includeSections.executiveSummary}
                      onChange={(e) =>
                        setConfig({
                          ...config,
                          includeSections: { ...config.includeSections, executiveSummary: e.target.checked },
                        })
                      }
                    />
                  }
                  label="Executive Summary"
                />
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={config.includeSections.performanceTrends}
                      onChange={(e) =>
                        setConfig({
                          ...config,
                          includeSections: { ...config.includeSections, performanceTrends: e.target.checked },
                        })
                      }
                    />
                  }
                  label="Performance Trends"
                />
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={config.includeSections.aiInsights}
                      onChange={(e) =>
                        setConfig({
                          ...config,
                          includeSections: { ...config.includeSections, aiInsights: e.target.checked },
                        })
                      }
                    />
                  }
                  label="AI Insights & Recommendations"
                />
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={config.includeSections.topCampaigns}
                      onChange={(e) =>
                        setConfig({
                          ...config,
                          includeSections: { ...config.includeSections, topCampaigns: e.target.checked },
                        })
                      }
                    />
                  }
                  label="Top Performing Campaigns"
                />
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={config.includeSections.improvements}
                      onChange={(e) =>
                        setConfig({
                          ...config,
                          includeSections: { ...config.includeSections, improvements: e.target.checked },
                        })
                      }
                    />
                  }
                  label="Areas for Improvement"
                />
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={config.includeSections.budgetAnalysis}
                      onChange={(e) =>
                        setConfig({
                          ...config,
                          includeSections: { ...config.includeSections, budgetAnalysis: e.target.checked },
                        })
                      }
                    />
                  }
                  label="Budget Allocation Analysis"
                />
              </FormGroup>
            </Grid>
          </Grid>
        </Box>
      )}

      {activeStep === 2 && (
        <Box>
          {loading ? (
            <AILoadingState message="AI is generating your report..." size="large" variant="pulse" />
          ) : generatedReport ? (
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">✅ Report Generated Successfully!</Typography>
                <Box sx={{ display: 'flex', gap: 2 }}>
                  <Button variant="contained" onClick={downloadPDF}>
                    Download PDF
                  </Button>
                  <Button variant="outlined" onClick={shareReport}>
                    Share Link
                  </Button>
                </Box>
              </Box>

              <GradientCard variant="ai" intensity="subtle">
                <CardContent>
                  <Box sx={{ mb: 3 }}>
                    <ReactMarkdown>{generatedReport.narrative}</ReactMarkdown>
                  </Box>

                  <Divider sx={{ my: 3 }} />

                  <Typography variant="h6" sx={{ mb: 2 }}>
                    Performance Trends
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={generatedReport.chart_data}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis yAxisId="left" />
                      <YAxis yAxisId="right" orientation="right" />
                      <Tooltip />
                      <Legend />
                      <Line yAxisId="left" type="monotone" dataKey="spend" stroke={colors.error.main} name="Spend (₹)" />
                      <Line yAxisId="left" type="monotone" dataKey="revenue" stroke={colors.success.main} name="Revenue (₹)" />
                      <Line yAxisId="right" type="monotone" dataKey="roas" stroke={colors.primary.main} name="ROAS" />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </GradientCard>
            </Box>
          ) : null}
        </Box>
      )}

      {/* Navigation Buttons */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
        <Button disabled={activeStep === 0} onClick={handleBack}>
          Back
        </Button>
        <Button
          variant="contained"
          onClick={handleNext}
          disabled={activeStep === 0 && !selectedType}
        >
          {activeStep === steps.length - 1 ? 'Start New Report' : activeStep === steps.length - 2 ? 'Generate Report' : 'Continue'}
        </Button>
      </Box>
    </Box>
  );
};

export default AIReportsPage;
