// Brand Setup Wizard - One-time configuration for AI ad generation
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
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Stack,
  Alert,
  CircularProgress,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useFilters } from '../../../context/FilterContext';
import { useSnackbar } from 'notistack';
import axios from 'axios';
import { AIBadge } from '../../ai/shared';

const API_BASE = 'http://localhost:8000/api/ai/ad-creator';

const steps = ['Company Info', 'Brand Voice', 'Target Audience', 'Ad Preferences'];

export const BrandSetupWizard: React.FC = () => {
  const { filters } = useFilters();
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();

  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [savingProfile, setSavingProfile] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    company_name: '',
    industry: '',
    website_url: '',
    product_category: '',
    price_range: 'mid-range',

    brand_voice: 'professional',
    tone_attributes: [] as string[],
    key_values: [] as string[],
    unique_selling_points: [] as string[],

    target_audience_description: '',
    audience_pain_points: [] as string[],

    preferred_ctas: ['Shop Now', 'Learn More'],
    prohibited_words: [] as string[],
    meta_page_id: '',
    image_style_preference: 'professional',
  });

  // Input helpers for chip arrays
  const [uspInput, setUspInput] = useState('');
  const [toneInput, setToneInput] = useState('');
  const [valueInput, setValueInput] = useState('');
  const [painPointInput, setPainPointInput] = useState('');
  const [ctaInput, setCtaInput] = useState('');
  const [prohibitedInput, setProhibitedInput] = useState('');

  // Load existing profile if available
  useEffect(() => {
    if (filters.customerId) {
      loadExistingProfile();
    }
  }, [filters.customerId]);

  const loadExistingProfile = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/brand-profile/${filters.customerId}`);

      if (response.data) {
        setFormData({
          company_name: response.data.company_name || '',
          industry: response.data.industry || '',
          website_url: response.data.website_url || '',
          product_category: response.data.product_category || '',
          price_range: response.data.price_range || 'mid-range',
          brand_voice: response.data.brand_voice || 'professional',
          tone_attributes: response.data.tone_attributes || [],
          key_values: response.data.key_values || [],
          unique_selling_points: response.data.unique_selling_points || [],
          target_audience_description: response.data.target_audience_description || '',
          audience_pain_points: response.data.audience_pain_points || [],
          preferred_ctas: response.data.preferred_ctas || ['Shop Now', 'Learn More'],
          prohibited_words: response.data.prohibited_words || [],
          meta_page_id: response.data.meta_page_id || '',
          image_style_preference: response.data.image_style_preference || 'professional',
        });
      }
    } catch (error: any) {
      if (error.response?.status !== 404) {
        console.error('Error loading profile:', error);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleAddChip = (
    value: string,
    setValue: React.Dispatch<React.SetStateAction<string>>,
    arrayKey: keyof typeof formData
  ) => {
    if (value.trim()) {
      setFormData({
        ...formData,
        [arrayKey]: [...(formData[arrayKey] as string[]), value.trim()]
      });
      setValue('');
    }
  };

  const handleDeleteChip = (arrayKey: keyof typeof formData, index: number) => {
    const newArray = [...(formData[arrayKey] as string[])];
    newArray.splice(index, 1);
    setFormData({
      ...formData,
      [arrayKey]: newArray
    });
  };

  const handleSubmit = async () => {
    if (!filters.customerId) {
      enqueueSnackbar('Please select a customer first', { variant: 'error' });
      return;
    }

    try {
      setSavingProfile(true);

      await axios.post(`${API_BASE}/brand-profile`, {
        customer_id: filters.customerId,
        ...formData
      });

      enqueueSnackbar('Brand profile saved successfully!', { variant: 'success' });

      // Navigate to AI Ad Creator
      navigate('/ai/ad-creator');
    } catch (error: any) {
      console.error('Error saving profile:', error);
      enqueueSnackbar(error.response?.data?.detail || 'Failed to save profile', { variant: 'error' });
    } finally {
      setSavingProfile(false);
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
                label="Company Name"
                value={formData.company_name}
                onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Industry</InputLabel>
                <Select
                  value={formData.industry}
                  onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                  label="Industry"
                >
                  <MenuItem value="ecommerce">E-commerce</MenuItem>
                  <MenuItem value="b2b-saas">B2B SaaS</MenuItem>
                  <MenuItem value="local-business">Local Business</MenuItem>
                  <MenuItem value="fashion">Fashion & Apparel</MenuItem>
                  <MenuItem value="electronics">Electronics</MenuItem>
                  <MenuItem value="health">Health & Wellness</MenuItem>
                  <MenuItem value="education">Education</MenuItem>
                  <MenuItem value="services">Professional Services</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Website URL"
                value={formData.website_url}
                onChange={(e) => setFormData({ ...formData, website_url: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Product Category"
                value={formData.product_category}
                onChange={(e) => setFormData({ ...formData, product_category: e.target.value })}
                placeholder="e.g., Sustainable Fashion, Cloud Software, Home Decor"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Price Range</InputLabel>
                <Select
                  value={formData.price_range}
                  onChange={(e) => setFormData({ ...formData, price_range: e.target.value })}
                  label="Price Range"
                >
                  <MenuItem value="budget">Budget (Under $50)</MenuItem>
                  <MenuItem value="mid-range">Mid-Range ($50-$200)</MenuItem>
                  <MenuItem value="premium">Premium ($200-$1000)</MenuItem>
                  <MenuItem value="luxury">Luxury ($1000+)</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        );

      case 1:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Brand Voice</InputLabel>
                <Select
                  value={formData.brand_voice}
                  onChange={(e) => setFormData({ ...formData, brand_voice: e.target.value })}
                  label="Brand Voice"
                >
                  <MenuItem value="professional">Professional</MenuItem>
                  <MenuItem value="casual">Casual & Friendly</MenuItem>
                  <MenuItem value="urgent">Urgent & Action-Driven</MenuItem>
                  <MenuItem value="luxurious">Luxurious & Premium</MenuItem>
                  <MenuItem value="playful">Playful & Fun</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Image Style</InputLabel>
                <Select
                  value={formData.image_style_preference}
                  onChange={(e) => setFormData({ ...formData, image_style_preference: e.target.value })}
                  label="Image Style"
                >
                  <MenuItem value="minimalist">Minimalist</MenuItem>
                  <MenuItem value="bold">Bold & Vibrant</MenuItem>
                  <MenuItem value="colorful">Colorful</MenuItem>
                  <MenuItem value="professional">Professional</MenuItem>
                  <MenuItem value="luxurious">Luxurious</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>Tone Attributes</Typography>
              <TextField
                fullWidth
                size="small"
                placeholder="Add tone (e.g., helpful, innovative, trustworthy)"
                value={toneInput}
                onChange={(e) => setToneInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddChip(toneInput, setToneInput, 'tone_attributes');
                  }
                }}
              />
              <Stack direction="row" spacing={1} sx={{ mt: 1, flexWrap: 'wrap' }}>
                {formData.tone_attributes.map((tone, index) => (
                  <Chip
                    key={index}
                    label={tone}
                    onDelete={() => handleDeleteChip('tone_attributes', index)}
                    sx={{ mb: 1 }}
                  />
                ))}
              </Stack>
            </Grid>

            <Grid item xs={12}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>Key Values</Typography>
              <TextField
                fullWidth
                size="small"
                placeholder="Add value (e.g., quality, affordability, sustainability)"
                value={valueInput}
                onChange={(e) => setValueInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddChip(valueInput, setValueInput, 'key_values');
                  }
                }}
              />
              <Stack direction="row" spacing={1} sx={{ mt: 1, flexWrap: 'wrap' }}>
                {formData.key_values.map((value, index) => (
                  <Chip
                    key={index}
                    label={value}
                    onDelete={() => handleDeleteChip('key_values', index)}
                    color="primary"
                    sx={{ mb: 1 }}
                  />
                ))}
              </Stack>
            </Grid>

            <Grid item xs={12}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>Unique Selling Points</Typography>
              <TextField
                fullWidth
                size="small"
                placeholder="Add USP (e.g., free shipping, 24/7 support, money-back guarantee)"
                value={uspInput}
                onChange={(e) => setUspInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddChip(uspInput, setUspInput, 'unique_selling_points');
                  }
                }}
              />
              <Stack direction="row" spacing={1} sx={{ mt: 1, flexWrap: 'wrap' }}>
                {formData.unique_selling_points.map((usp, index) => (
                  <Chip
                    key={index}
                    label={usp}
                    onDelete={() => handleDeleteChip('unique_selling_points', index)}
                    color="secondary"
                    sx={{ mb: 1 }}
                  />
                ))}
              </Stack>
            </Grid>
          </Grid>
        );

      case 2:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Target Audience Description"
                value={formData.target_audience_description}
                onChange={(e) => setFormData({ ...formData, target_audience_description: e.target.value })}
                placeholder="e.g., Millennial women aged 25-45 interested in sustainable fashion and ethical brands"
                required
              />
            </Grid>

            <Grid item xs={12}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>Audience Pain Points</Typography>
              <TextField
                fullWidth
                size="small"
                placeholder="Add pain point (e.g., expensive shipping, sizing issues, limited options)"
                value={painPointInput}
                onChange={(e) => setPainPointInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddChip(painPointInput, setPainPointInput, 'audience_pain_points');
                  }
                }}
              />
              <Stack direction="row" spacing={1} sx={{ mt: 1, flexWrap: 'wrap' }}>
                {formData.audience_pain_points.map((pain, index) => (
                  <Chip
                    key={index}
                    label={pain}
                    onDelete={() => handleDeleteChip('audience_pain_points', index)}
                    color="warning"
                    sx={{ mb: 1 }}
                  />
                ))}
              </Stack>
            </Grid>
          </Grid>
        );

      case 3:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>Preferred Call-to-Actions</Typography>
              <TextField
                fullWidth
                size="small"
                placeholder="Add CTA (e.g., Shop Now, Learn More, Get Started)"
                value={ctaInput}
                onChange={(e) => setCtaInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddChip(ctaInput, setCtaInput, 'preferred_ctas');
                  }
                }}
              />
              <Stack direction="row" spacing={1} sx={{ mt: 1, flexWrap: 'wrap' }}>
                {formData.preferred_ctas.map((cta, index) => (
                  <Chip
                    key={index}
                    label={cta}
                    onDelete={() => handleDeleteChip('preferred_ctas', index)}
                    color="success"
                    sx={{ mb: 1 }}
                  />
                ))}
              </Stack>
            </Grid>

            <Grid item xs={12}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>Prohibited Words (Optional)</Typography>
              <TextField
                fullWidth
                size="small"
                placeholder="Words to avoid (e.g., cheap, discount, limited)"
                value={prohibitedInput}
                onChange={(e) => setProhibitedInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddChip(prohibitedInput, setProhibitedInput, 'prohibited_words');
                  }
                }}
              />
              <Stack direction="row" spacing={1} sx={{ mt: 1, flexWrap: 'wrap' }}>
                {formData.prohibited_words.map((word, index) => (
                  <Chip
                    key={index}
                    label={word}
                    onDelete={() => handleDeleteChip('prohibited_words', index)}
                    color="error"
                    variant="outlined"
                    sx={{ mb: 1 }}
                  />
                ))}
              </Stack>
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Meta (Facebook) Page ID"
                value={formData.meta_page_id}
                onChange={(e) => setFormData({ ...formData, meta_page_id: e.target.value })}
                placeholder="e.g., 123456789012345"
                helperText="Required for posting ads to Meta. Find it in your Facebook Page settings."
              />
            </Grid>
          </Grid>
        );

      default:
        return null;
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 600, mb: 1 }}>
            Brand Setup Wizard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Configure your brand profile once for AI-powered ad generation
          </Typography>
        </Box>
        <AIBadge />
      </Box>

      {!filters.customerId && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          Please select a customer to configure brand profile
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
        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Button
            disabled={activeStep === 0}
            onClick={handleBack}
          >
            Back
          </Button>

          <Box>
            {activeStep === steps.length - 1 ? (
              <Button
                variant="contained"
                onClick={handleSubmit}
                disabled={savingProfile || !filters.customerId}
              >
                {savingProfile ? <CircularProgress size={24} /> : 'Save & Continue'}
              </Button>
            ) : (
              <Button
                variant="contained"
                onClick={handleNext}
              >
                Next
              </Button>
            )}
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default BrandSetupWizard;
