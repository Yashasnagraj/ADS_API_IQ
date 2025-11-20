// AI Ad Creator - 4-Step Workflow for Madgicx-style ad generation and launch
import React, { useState, useEffect } from 'react';
import {
  Box,
  Stepper,
  Step,
  StepLabel,
  Button,
  Typography,
  TextField,
  Paper,
  Grid,
  Card,
  CardContent,
  CardMedia,
  CardActions,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  CircularProgress,
  Chip,
  Rating,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
} from '@mui/material';
import {
  AutoAwesome as SparklesIcon,
  Edit as EditIcon,
  CheckCircle as CheckIcon,
  RocketLaunch as LaunchIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useFilters } from '../../../context/FilterContext';
import { useSnackbar } from 'notistack';
import axios from 'axios';
import { AIBadge, AILoadingState } from '../../ai/shared';

const API_BASE = 'http://localhost:8000/api/ai/ad-creator';

const steps = ['Campaign Brief', 'AI Generation', 'Review & Edit', 'Launch'];

interface AdVariation {
  variation_id: number;
  primary_text: string;
  headline: string;
  description: string;
  cta: string;
  image_url: string | null;
  confidence_score: number;
  focus_usp: string;
}

export const AIAdCreatorPage: React.FC = () => {
  const { filters } = useFilters();
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();

  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [launching, setLaunching] = useState(false);

  // Step 1: Campaign Brief
  const [briefData, setBriefData] = useState({
    product_name: '',
    product_description: '',
    campaign_goal: 'sales',
    landing_url: '',
    daily_budget_usd: 10,
    num_variations: 5,
    generate_images: true,
  });

  // Step 2 & 3: Generated Variations
  const [variations, setVariations] = useState<AdVariation[]>([]);
  const [selectedVariation, setSelectedVariation] = useState<AdVariation | null>(null);

  // Step 3: Edit Dialog
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editedAd, setEditedAd] = useState<AdVariation | null>(null);

  // Step 4: Launch Configuration
  const [launchConfig, setLaunchConfig] = useState({
    meta_account_id: '',
    campaign_name: '',
    target_countries: ['US'],
    target_age_min: 18,
    target_age_max: 65,
  });

  const [launchResult, setLaunchResult] = useState<any>(null);

  // Check if brand profile exists
  useEffect(() => {
    if (filters.customerId) {
      checkBrandProfile();
    }
  }, [filters.customerId]);

  const checkBrandProfile = async () => {
    try {
      await axios.get(`${API_BASE}/brand-profile/${filters.customerId}`);
    } catch (error: any) {
      if (error.response?.status === 404) {
        enqueueSnackbar('Please complete brand setup first', { variant: 'warning' });
        navigate('/ai/brand-setup');
      }
    }
  };

  const handleNext = () => {
    setActiveStep((prev) => prev + 1);
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
  };

  const handleGenerateAds = async () => {
    if (!filters.customerId) {
      enqueueSnackbar('Please select a customer', { variant: 'error' });
      return;
    }

    try {
      setGenerating(true);

      const response = await axios.post(`${API_BASE}/generate`, {
        customer_id: filters.customerId,
        ...briefData,
      });

      setVariations(response.data.variations);
      enqueueSnackbar(`Generated ${response.data.total_count} ad variations!`, { variant: 'success' });
      handleNext();
    } catch (error: any) {
      console.error('Error generating ads:', error);
      enqueueSnackbar(error.response?.data?.detail || 'Failed to generate ads', { variant: 'error' });
    } finally {
      setGenerating(false);
    }
  };

  const handleSelectVariation = (variation: AdVariation) => {
    setSelectedVariation(variation);
    setLaunchConfig({
      ...launchConfig,
      campaign_name: `${briefData.product_name} - ${new Date().toLocaleDateString()}`,
    });
    handleNext();
  };

  const handleEditVariation = (variation: AdVariation) => {
    setEditedAd({ ...variation });
    setEditDialogOpen(true);
  };

  const handleSaveEdit = () => {
    if (editedAd) {
      const updatedVariations = variations.map((v) =>
        v.variation_id === editedAd.variation_id ? editedAd : v
      );
      setVariations(updatedVariations);

      if (selectedVariation?.variation_id === editedAd.variation_id) {
        setSelectedVariation(editedAd);
      }

      enqueueSnackbar('Ad variation updated', { variant: 'success' });
    }
    setEditDialogOpen(false);
  };

  const handleLaunchAd = async () => {
    if (!selectedVariation || !filters.customerId) {
      enqueueSnackbar('Missing required data', { variant: 'error' });
      return;
    }

    if (!launchConfig.meta_account_id) {
      enqueueSnackbar('Please enter Meta Account ID', { variant: 'error' });
      return;
    }

    try {
      setLaunching(true);

      const response = await axios.post(`${API_BASE}/launch`, {
        customer_id: filters.customerId,
        meta_account_id: launchConfig.meta_account_id,
        campaign_name: launchConfig.campaign_name,
        product_name: briefData.product_name,
        landing_url: briefData.landing_url,
        daily_budget_usd: briefData.daily_budget_usd,
        primary_text: selectedVariation.primary_text,
        headline: selectedVariation.headline,
        description: selectedVariation.description,
        cta: selectedVariation.cta,
        image_url: selectedVariation.image_url,
        target_countries: launchConfig.target_countries,
        target_age_min: launchConfig.target_age_min,
        target_age_max: launchConfig.target_age_max,
      });

      setLaunchResult(response.data);
      enqueueSnackbar('Ad launched successfully to Meta Ads!', { variant: 'success' });
      handleNext();
    } catch (error: any) {
      console.error('Error launching ad:', error);
      enqueueSnackbar(error.response?.data?.detail || 'Failed to launch ad', { variant: 'error' });
    } finally {
      setLaunching(false);
    }
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Product/Service Name"
                value={briefData.product_name}
                onChange={(e) => setBriefData({ ...briefData, product_name: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Product Description"
                value={briefData.product_description}
                onChange={(e) => setBriefData({ ...briefData, product_description: e.target.value })}
                placeholder="Describe your product, its benefits, and what makes it unique"
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Campaign Goal</InputLabel>
                <Select
                  value={briefData.campaign_goal}
                  onChange={(e) => setBriefData({ ...briefData, campaign_goal: e.target.value })}
                  label="Campaign Goal"
                >
                  <MenuItem value="sales">Sales</MenuItem>
                  <MenuItem value="leads">Lead Generation</MenuItem>
                  <MenuItem value="traffic">Website Traffic</MenuItem>
                  <MenuItem value="awareness">Brand Awareness</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Landing URL"
                value={briefData.landing_url}
                onChange={(e) => setBriefData({ ...briefData, landing_url: e.target.value })}
                placeholder="https://yourwebsite.com/product"
                required
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                type="number"
                label="Daily Budget (USD)"
                value={briefData.daily_budget_usd}
                onChange={(e) => setBriefData({ ...briefData, daily_budget_usd: Number(e.target.value) })}
                InputProps={{ inputProps: { min: 1 } }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                type="number"
                label="Number of Variations"
                value={briefData.num_variations}
                onChange={(e) => setBriefData({ ...briefData, num_variations: Number(e.target.value) })}
                InputProps={{ inputProps: { min: 1, max: 10 } }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Generate Images</InputLabel>
                <Select
                  value={briefData.generate_images ? 'yes' : 'no'}
                  onChange={(e) => setBriefData({ ...briefData, generate_images: e.target.value === 'yes' })}
                  label="Generate Images"
                >
                  <MenuItem value="yes">Yes (AI-generated)</MenuItem>
                  <MenuItem value="no">No (I'll upload later)</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <Button
                variant="contained"
                size="large"
                fullWidth
                onClick={handleGenerateAds}
                disabled={!briefData.product_name || !briefData.product_description || !briefData.landing_url || generating}
                startIcon={generating ? <CircularProgress size={20} /> : <SparklesIcon />}
                sx={{ mt: 2 }}
              >
                {generating ? 'Generating with AI...' : 'Generate Ad Variations'}
              </Button>
            </Grid>
          </Grid>
        );

      case 1:
        return (
          <Box>
            {generating ? (
              <Box sx={{ py: 8 }}>
                <AILoadingState message="AI is crafting your ad variations..." variant="pulse" />
              </Box>
            ) : (
              <Grid container spacing={3}>
                {variations.map((variation) => (
                  <Grid item xs={12} md={6} key={variation.variation_id}>
                    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                      {variation.image_url && (
                        <CardMedia
                          component="img"
                          height="200"
                          image={variation.image_url}
                          alt="Ad creative"
                        />
                      )}
                      <CardContent sx={{ flexGrow: 1 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                          <Typography variant="caption" color="text.secondary">
                            Variation #{variation.variation_id}
                          </Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Rating value={variation.confidence_score / 2} precision={0.5} size="small" readOnly />
                            <Typography variant="caption">
                              {variation.confidence_score}/10
                            </Typography>
                          </Box>
                        </Box>

                        <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>
                          {variation.primary_text}
                        </Typography>
                        <Typography variant="subtitle2" sx={{ mb: 0.5 }}>
                          {variation.headline}
                        </Typography>
                        <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                          {variation.description}
                        </Typography>

                        <Chip label={variation.cta} size="small" color="primary" sx={{ mt: 1 }} />
                        <Chip label={`Focus: ${variation.focus_usp}`} size="small" variant="outlined" sx={{ mt: 1, ml: 1 }} />
                      </CardContent>
                      <CardActions>
                        <Button size="small" startIcon={<EditIcon />} onClick={() => handleEditVariation(variation)}>
                          Edit
                        </Button>
                        <Button size="small" variant="contained" startIcon={<CheckIcon />} onClick={() => handleSelectVariation(variation)}>
                          Select
                        </Button>
                      </CardActions>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            )}
          </Box>
        );

      case 2:
        return (
          <Box>
            {selectedVariation && (
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  {selectedVariation.image_url && (
                    <Box
                      component="img"
                      src={selectedVariation.image_url}
                      alt="Selected ad"
                      sx={{ width: '100%', borderRadius: 2, mb: 2 }}
                    />
                  )}
                </Grid>
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 3 }}>
                    <Typography variant="h6" sx={{ mb: 2 }}>
                      Selected Ad Preview
                    </Typography>

                    <Box sx={{ mb: 2 }}>
                      <Typography variant="caption" color="text.secondary">
                        Primary Text
                      </Typography>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        {selectedVariation.primary_text}
                      </Typography>
                    </Box>

                    <Box sx={{ mb: 2 }}>
                      <Typography variant="caption" color="text.secondary">
                        Headline
                      </Typography>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        {selectedVariation.headline}
                      </Typography>
                    </Box>

                    <Box sx={{ mb: 2 }}>
                      <Typography variant="caption" color="text.secondary">
                        Description
                      </Typography>
                      <Typography variant="body2">
                        {selectedVariation.description}
                      </Typography>
                    </Box>

                    <Box sx={{ mb: 2 }}>
                      <Typography variant="caption" color="text.secondary">
                        Call-to-Action
                      </Typography>
                      <Box sx={{ mt: 0.5 }}>
                        <Chip label={selectedVariation.cta} color="primary" />
                      </Box>
                    </Box>

                    <Box sx={{ display: 'flex', gap: 1, mt: 3 }}>
                      <Button variant="outlined" startIcon={<EditIcon />} onClick={() => handleEditVariation(selectedVariation)}>
                        Edit
                      </Button>
                      <Button variant="outlined" onClick={() => setActiveStep(1)}>
                        Choose Different
                      </Button>
                    </Box>
                  </Paper>
                </Grid>

                <Grid item xs={12}>
                  <Alert severity="info" sx={{ mt: 2 }}>
                    Review your ad carefully before launching. You can edit any element or go back to choose a different variation.
                  </Alert>
                </Grid>
              </Grid>
            )}
          </Box>
        );

      case 3:
        return (
          <Box>
            {launchResult ? (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <CheckIcon sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
                <Typography variant="h5" sx={{ mb: 2 }}>
                  Ad Launched Successfully!
                </Typography>
                <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                  Your ad has been created in Meta Ads Manager in PAUSED state for your review.
                </Typography>

                <Paper sx={{ p: 3, maxWidth: 600, mx: 'auto', textAlign: 'left' }}>
                  <Typography variant="subtitle2" sx={{ mb: 1 }}>
                    Campaign Details:
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 0.5 }}>
                    Campaign ID: {launchResult.campaign_id}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 0.5 }}>
                    Ad Set ID: {launchResult.ad_set_id}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    Ad ID: {launchResult.ad_id}
                  </Typography>

                  <Button
                    variant="contained"
                    href={launchResult.meta_ads_url}
                    target="_blank"
                    fullWidth
                  >
                    View in Meta Ads Manager
                  </Button>
                </Paper>

                <Button
                  variant="outlined"
                  onClick={() => {
                    setActiveStep(0);
                    setVariations([]);
                    setSelectedVariation(null);
                    setLaunchResult(null);
                  }}
                  sx={{ mt: 3 }}
                >
                  Create Another Ad
                </Button>
              </Box>
            ) : (
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <Alert severity="warning" sx={{ mb: 2 }}>
                    Your ad will be created in PAUSED state. Review it in Meta Ads Manager before activating.
                  </Alert>
                </Grid>

                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Meta Account ID"
                    value={launchConfig.meta_account_id}
                    onChange={(e) => setLaunchConfig({ ...launchConfig, meta_account_id: e.target.value })}
                    placeholder="act_123456789"
                    required
                    helperText="Format: act_XXXXXXXXXX"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Campaign Name"
                    value={launchConfig.campaign_name}
                    onChange={(e) => setLaunchConfig({ ...launchConfig, campaign_name: e.target.value })}
                    required
                  />
                </Grid>

                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Target Age Min"
                    value={launchConfig.target_age_min}
                    onChange={(e) => setLaunchConfig({ ...launchConfig, target_age_min: Number(e.target.value) })}
                    InputProps={{ inputProps: { min: 13, max: 65 } }}
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Target Age Max"
                    value={launchConfig.target_age_max}
                    onChange={(e) => setLaunchConfig({ ...launchConfig, target_age_max: Number(e.target.value) })}
                    InputProps={{ inputProps: { min: 13, max: 65 } }}
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <FormControl fullWidth>
                    <InputLabel>Target Country</InputLabel>
                    <Select
                      value={launchConfig.target_countries[0]}
                      onChange={(e) => setLaunchConfig({ ...launchConfig, target_countries: [e.target.value] })}
                      label="Target Country"
                    >
                      <MenuItem value="US">United States</MenuItem>
                      <MenuItem value="GB">United Kingdom</MenuItem>
                      <MenuItem value="CA">Canada</MenuItem>
                      <MenuItem value="AU">Australia</MenuItem>
                      <MenuItem value="IN">India</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12}>
                  <Button
                    variant="contained"
                    size="large"
                    fullWidth
                    onClick={handleLaunchAd}
                    disabled={!launchConfig.meta_account_id || !launchConfig.campaign_name || launching}
                    startIcon={launching ? <CircularProgress size={20} /> : <LaunchIcon />}
                    sx={{ mt: 2 }}
                  >
                    {launching ? 'Launching to Meta...' : 'Launch Ad to Meta Ads'}
                  </Button>
                </Grid>
              </Grid>
            )}
          </Box>
        );

      default:
        return null;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 600, mb: 1 }}>
            AI Ad Creator
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Generate and launch high-converting Meta ads with AI
          </Typography>
        </Box>
        <AIBadge />
      </Box>

      {!filters.customerId && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          Please select a customer to create ads
        </Alert>
      )}

      <Paper sx={{ p: 4 }}>
        {/* Stepper */}
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {/* Step Content */}
        <Box sx={{ minHeight: 400, mb: 3 }}>
          {renderStepContent(activeStep)}
        </Box>

        {/* Navigation Buttons */}
        {activeStep < 3 && (
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
            <Button disabled={activeStep === 0} onClick={handleBack}>
              Back
            </Button>
            {activeStep > 0 && activeStep < 3 && (
              <Button variant="contained" onClick={handleNext} disabled={!selectedVariation && activeStep === 2}>
                {activeStep === 2 ? 'Continue to Launch' : 'Continue'}
              </Button>
            )}
          </Box>
        )}
      </Paper>

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Ad Variation</DialogTitle>
        <DialogContent>
          {editedAd && (
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Primary Text"
                  value={editedAd.primary_text}
                  onChange={(e) => setEditedAd({ ...editedAd, primary_text: e.target.value.slice(0, 125) })}
                  helperText={`${editedAd.primary_text.length}/125 characters`}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Headline"
                  value={editedAd.headline}
                  onChange={(e) => setEditedAd({ ...editedAd, headline: e.target.value.slice(0, 27) })}
                  helperText={`${editedAd.headline.length}/27 characters`}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Description"
                  value={editedAd.description}
                  onChange={(e) => setEditedAd({ ...editedAd, description: e.target.value.slice(0, 27) })}
                  helperText={`${editedAd.description.length}/27 characters`}
                />
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveEdit}>
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AIAdCreatorPage;
