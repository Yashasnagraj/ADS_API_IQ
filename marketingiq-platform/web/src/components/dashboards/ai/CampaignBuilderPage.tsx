import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stepper,
  Step,
  StepLabel,
  Divider,
  Chip,
  Stack,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  FormControlLabel,
  Switch,
  Alert,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch';
import SettingsIcon from '@mui/icons-material/Settings';
import PreviewIcon from '@mui/icons-material/Preview';
import TipsAndUpdatesIcon from '@mui/icons-material/TipsAndUpdates';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import GroupWorkIcon from '@mui/icons-material/GroupWork';
import { AIBadge, AILoadingState, GradientCard, ConfidenceScore } from '../../ai/shared';
import { EmptyState } from '../../common/EmptyState';
import { useFilters } from '../../../context/FilterContext';
import { colors, shadows } from '../../../theme/designTokens';
import { useSnackbar } from 'notistack';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/ai';

const steps = ['Select Template', 'Configure Campaign', 'Review Structure'];

export const CampaignBuilderPage: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [templates, setTemplates] = useState<any[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [generatedCampaign, setGeneratedCampaign] = useState<any>(null);
  const { filters } = useFilters();
  const { enqueueSnackbar } = useSnackbar();

  const [config, setConfig] = useState({
    businessType: 'ecommerce',
    goal: 'sales',
    budget: 1000,
    targetLocation: 'India',
    productService: '',
    useBestPractices: true,
  });

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await axios.get(`${API_BASE}/campaign-builder/templates`);
      setTemplates(response.data.templates || []);
    } catch (error) {
      console.error('Error loading templates:', error);
    }
  };

  const handleNext = async () => {
    if (activeStep === steps.length - 2) {
      await generateCampaign();
    }
    setActiveStep((prev) => prev + 1);
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
  };

  const handleReset = () => {
    setActiveStep(0);
    setSelectedTemplate('');
    setGeneratedCampaign(null);
  };

  const generateCampaign = async () => {
    if (!filters.customerId) {
      enqueueSnackbar('Please select a customer first', { variant: 'warning' });
      return;
    }

    if (!config.productService) {
      enqueueSnackbar('Please enter product/service name', { variant: 'warning' });
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/campaign-builder/generate`, {
        customer_id: filters.customerId,
        business_type: config.businessType,
        goal: config.goal,
        budget: config.budget,
        target_location: config.targetLocation,
        product_service: config.productService,
        use_best_practices: config.useBestPractices,
      });

      setGeneratedCampaign(response.data);
      enqueueSnackbar('Campaign structure generated successfully!', { variant: 'success' });
    } catch (error) {
      console.error('Error generating campaign:', error);
      enqueueSnackbar('Failed to generate campaign structure', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 600, mb: 1 }}>
            AI Campaign Builder
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Build optimized campaign structures with AI-powered recommendations
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
            Select Campaign Template
          </Typography>
          <Grid container spacing={3}>
            {templates.map((template) => (
              <Grid item xs={12} md={6} key={template.id}>
                <Card
                  sx={{
                    cursor: 'pointer',
                    border:
                      selectedTemplate === template.id ? `2px solid ${colors.primary.main}` : '2px solid transparent',
                    transition: 'all 0.3s',
                    height: '100%',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: shadows.lg,
                    },
                  }}
                  onClick={() => {
                    setSelectedTemplate(template.id);
                    setConfig({ ...config, businessType: template.id.split('_')[0] });
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                      <GroupWorkIcon sx={{ fontSize: 40, color: colors.primary.main }} />
                      <Box>
                        <Typography variant="h6">{template.name}</Typography>
                        <Chip label={template.budget_range} size="small" sx={{ mt: 0.5 }} />
                      </Box>
                    </Box>

                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {template.description}
                    </Typography>

                    <Divider sx={{ my: 2 }} />

                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                      Campaign Structure:
                    </Typography>
                    <Grid container spacing={1} sx={{ mb: 2 }}>
                      <Grid item xs={6}>
                        <Typography variant="caption">
                          {template.structure.campaigns} Campaigns
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="caption">
                          {template.structure.ad_groups_per_campaign} Ad Groups
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="caption">
                          {template.structure.keywords_per_ad_group} Keywords
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="caption">
                          {template.structure.ads_per_ad_group} Ads
                        </Typography>
                      </Grid>
                    </Grid>

                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                      Best For:
                    </Typography>
                    <Stack direction="row" flexWrap="wrap" gap={0.5} sx={{ mb: 2 }}>
                      {template.best_for.map((item: string, i: number) => (
                        <Chip key={i} label={item} size="small" variant="outlined" />
                      ))}
                    </Stack>

                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                      Features:
                    </Typography>
                    <List dense>
                      {template.features.slice(0, 3).map((feature: string, i: number) => (
                        <ListItem key={i} sx={{ py: 0 }}>
                          <ListItemIcon sx={{ minWidth: 30 }}>
                            <CheckCircleIcon sx={{ fontSize: 16, color: colors.success.main }} />
                          </ListItemIcon>
                          <ListItemText
                            primary={<Typography variant="caption">{feature}</Typography>}
                          />
                        </ListItem>
                      ))}
                    </List>
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
            Configure Campaign Settings
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <GradientCard variant="ai" intensity="subtle">
                <CardContent>
                  <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                    Basic Settings
                  </Typography>

                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel>Business Type</InputLabel>
                    <Select
                      value={config.businessType}
                      onChange={(e) => setConfig({ ...config, businessType: e.target.value })}
                      label="Business Type"
                    >
                      <MenuItem value="ecommerce">E-commerce</MenuItem>
                      <MenuItem value="b2b">B2B</MenuItem>
                      <MenuItem value="local">Local Business</MenuItem>
                      <MenuItem value="saas">SaaS</MenuItem>
                    </Select>
                  </FormControl>

                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel>Campaign Goal</InputLabel>
                    <Select
                      value={config.goal}
                      onChange={(e) => setConfig({ ...config, goal: e.target.value })}
                      label="Campaign Goal"
                    >
                      <MenuItem value="sales">Sales</MenuItem>
                      <MenuItem value="leads">Lead Generation</MenuItem>
                      <MenuItem value="awareness">Brand Awareness</MenuItem>
                      <MenuItem value="app_installs">App Installs</MenuItem>
                    </Select>
                  </FormControl>

                  <TextField
                    fullWidth
                    label="Product/Service Name"
                    value={config.productService}
                    onChange={(e) => setConfig({ ...config, productService: e.target.value })}
                    sx={{ mb: 2 }}
                    required
                  />

                  <TextField
                    fullWidth
                    label="Daily Budget (₹)"
                    type="number"
                    value={config.budget}
                    onChange={(e) => setConfig({ ...config, budget: parseFloat(e.target.value) })}
                    sx={{ mb: 2 }}
                  />

                  <TextField
                    fullWidth
                    label="Target Location"
                    value={config.targetLocation}
                    onChange={(e) => setConfig({ ...config, targetLocation: e.target.value })}
                    sx={{ mb: 2 }}
                  />

                  <FormControlLabel
                    control={
                      <Switch
                        checked={config.useBestPractices}
                        onChange={(e) => setConfig({ ...config, useBestPractices: e.target.checked })}
                      />
                    }
                    label="Include Best Practices Recommendations"
                  />
                </CardContent>
              </GradientCard>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <TipsAndUpdatesIcon sx={{ color: colors.warning.main }} />
                    <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                      AI Recommendations
                    </Typography>
                  </Box>

                  <Alert severity="info" sx={{ mb: 2 }}>
                    Based on your selections, we'll create an optimized campaign structure for {config.businessType}{' '}
                    focused on {config.goal}.
                  </Alert>

                  <Typography variant="body2" sx={{ mb: 2 }}>
                    Your campaign will include:
                  </Typography>

                  <List dense>
                    <ListItem>
                      <ListItemIcon>
                        <CheckCircleIcon sx={{ color: colors.success.main }} />
                      </ListItemIcon>
                      <ListItemText primary="Optimized ad groups based on your product" />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <CheckCircleIcon sx={{ color: colors.success.main }} />
                      </ListItemIcon>
                      <ListItemText primary="Keyword suggestions with match types" />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <CheckCircleIcon sx={{ color: colors.success.main }} />
                      </ListItemIcon>
                      <ListItemText primary="Ad copy templates" />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <CheckCircleIcon sx={{ color: colors.success.main }} />
                      </ListItemIcon>
                      <ListItemText primary="Budget allocation recommendations" />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <CheckCircleIcon sx={{ color: colors.success.main }} />
                      </ListItemIcon>
                      <ListItemText primary="Performance predictions" />
                    </ListItem>
                  </List>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      )}

      {activeStep === 2 && (
        <Box>
          {loading ? (
            <AILoadingState message="AI is building your campaign structure..." size="large" variant="pulse" />
          ) : generatedCampaign ? (
            <Box>
              <Typography variant="h6" sx={{ mb: 3 }}>
                ✅ Campaign Structure Generated!
              </Typography>

              {/* Campaign Overview */}
              <GradientCard variant="success" intensity="subtle" sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="h5" sx={{ mb: 2, fontWeight: 600 }}>
                    {generatedCampaign.campaign_structure.campaign_name}
                  </Typography>

                  <Grid container spacing={3}>
                    <Grid item xs={12} md={4}>
                      <Typography variant="caption" color="text.secondary">
                        Daily Budget
                      </Typography>
                      <Typography variant="h6">₹{generatedCampaign.campaign_structure.budget.daily}</Typography>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Typography variant="caption" color="text.secondary">
                        Monthly Budget
                      </Typography>
                      <Typography variant="h6">₹{generatedCampaign.campaign_structure.budget.monthly}</Typography>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Typography variant="caption" color="text.secondary">
                        Ad Groups
                      </Typography>
                      <Typography variant="h6">{generatedCampaign.campaign_structure.ad_groups.length}</Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </GradientCard>

              {/* Performance Predictions */}
              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <TrendingUpIcon sx={{ color: colors.primary.main }} />
                    <Typography variant="h6">Performance Predictions</Typography>
                  </Box>

                  <Grid container spacing={2}>
                    <Grid item xs={6} md={3}>
                      <Box sx={{ textAlign: 'center', p: 2, bgcolor: colors.primary[50], borderRadius: 1 }}>
                        <Typography variant="h4" sx={{ color: colors.primary.main }}>
                          {generatedCampaign.predictions.estimated_daily_clicks}
                        </Typography>
                        <Typography variant="caption">Daily Clicks</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Box sx={{ textAlign: 'center', p: 2, bgcolor: colors.info[50], borderRadius: 1 }}>
                        <Typography variant="h4" sx={{ color: colors.info.main }}>
                          {generatedCampaign.predictions.estimated_daily_impressions}
                        </Typography>
                        <Typography variant="caption">Daily Impressions</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Box sx={{ textAlign: 'center', p: 2, bgcolor: colors.success[50], borderRadius: 1 }}>
                        <Typography variant="h4" sx={{ color: colors.success.main }}>
                          {generatedCampaign.predictions.estimated_conversions}
                        </Typography>
                        <Typography variant="caption">Monthly Conversions</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Box sx={{ textAlign: 'center', p: 2, bgcolor: colors.warning[50], borderRadius: 1 }}>
                        <Typography variant="h4" sx={{ color: colors.warning.main }}>
                          ₹{generatedCampaign.predictions.estimated_cpa}
                        </Typography>
                        <Typography variant="caption">Est. CPA</Typography>
                      </Box>
                    </Grid>
                  </Grid>

                  <Box sx={{ mt: 2 }}>
                    <ConfidenceScore value={generatedCampaign.predictions.confidence} label="Prediction Confidence" />
                  </Box>
                </CardContent>
              </Card>

              {/* Ad Groups */}
              <Typography variant="h6" sx={{ mb: 2 }}>
                Ad Groups Structure
              </Typography>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                {generatedCampaign.campaign_structure.ad_groups.map((ag: any, index: number) => (
                  <Grid item xs={12} md={6} key={index}>
                    <Card>
                      <CardContent>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
                          {ag.name}
                        </Typography>
                        <Chip label={ag.bid_strategy} size="small" color="primary" sx={{ mb: 2 }} />

                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                          Keywords:
                        </Typography>
                        <Stack direction="row" flexWrap="wrap" gap={0.5}>
                          {ag.keywords.map((kw: string, i: number) => (
                            <Chip key={i} label={kw} size="small" variant="outlined" />
                          ))}
                        </Stack>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>

              {/* Best Practices */}
              {generatedCampaign.best_practices && generatedCampaign.best_practices.length > 0 && (
                <Card sx={{ mb: 3 }}>
                  <CardContent>
                    <Typography variant="h6" sx={{ mb: 2 }}>
                      Best Practices
                    </Typography>
                    <List>
                      {generatedCampaign.best_practices.map((practice: string, i: number) => (
                        <ListItem key={i}>
                          <ListItemIcon>
                            <CheckCircleIcon sx={{ color: colors.success.main }} />
                          </ListItemIcon>
                          <ListItemText primary={practice} />
                        </ListItem>
                      ))}
                    </List>
                  </CardContent>
                </Card>
              )}

              {/* Historical Insights */}
              {generatedCampaign.historical_insights && generatedCampaign.historical_insights.top_keywords.length > 0 && (
                <Alert severity="info">
                  <Typography variant="subtitle2" sx={{ mb: 1 }}>
                    {generatedCampaign.historical_insights.message}
                  </Typography>
                  <Stack direction="row" flexWrap="wrap" gap={0.5}>
                    {generatedCampaign.historical_insights.top_keywords.map((kw: string, i: number) => (
                      <Chip key={i} label={kw} size="small" />
                    ))}
                  </Stack>
                </Alert>
              )}
            </Box>
          ) : null}
        </Box>
      )}

      {/* Navigation Buttons */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
        <Button disabled={activeStep === 0} onClick={handleBack}>
          Back
        </Button>
        <Box sx={{ display: 'flex', gap: 2 }}>
          {activeStep === steps.length - 1 && (
            <Button variant="outlined" onClick={handleReset}>
              Build Another Campaign
            </Button>
          )}
          <Button
            variant="contained"
            onClick={handleNext}
            disabled={(activeStep === 0 && !selectedTemplate) || (activeStep === 2 && !generatedCampaign)}
            startIcon={activeStep === steps.length - 2 ? <RocketLaunchIcon /> : undefined}
          >
            {activeStep === steps.length - 1
              ? 'Finish'
              : activeStep === steps.length - 2
              ? 'Generate Campaign'
              : 'Continue'}
          </Button>
        </Box>
      </Box>
    </Box>
  );
};

export default CampaignBuilderPage;
