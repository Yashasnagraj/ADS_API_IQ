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
  Chip,
  Divider,
  Paper,
  IconButton,
  Rating,
  Stack,
  Alert,
} from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import ThumbUpIcon from '@mui/icons-material/ThumbUp';
import EditIcon from '@mui/icons-material/Edit';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import VerifiedIcon from '@mui/icons-material/Verified';
import { AIBadge, AILoadingState, GradientCard, ConfidenceScore } from '../../ai/shared';
import { EmptyState } from '../../common/EmptyState';
import { useFilters } from '../../../context/FilterContext';
import { colors, shadows } from '../../../theme/designTokens';
import { useSnackbar } from 'notistack';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/ai';

export const CreativeStudioPage: React.FC = () => {
  const [mode, setMode] = useState<'generate' | 'optimize'>('generate');
  const [loading, setLoading] = useState(false);
  const [generatedAds, setGeneratedAds] = useState<any[]>([]);
  const [optimizedAds, setOptimizedAds] = useState<any>(null);
  const [topPerformers, setTopPerformers] = useState<any[]>([]);
  const { filters } = useFilters();
  const { enqueueSnackbar } = useSnackbar();

  // Generate form state
  const [generateForm, setGenerateForm] = useState({
    campaignGoal: 'sales',
    product: '',
    targetAudience: '',
    tone: 'professional',
    keyBenefits: [''],
    specialOffer: '',
  });

  // Optimize form state
  const [optimizeForm, setOptimizeForm] = useState({
    headline: '',
    description: '',
  });

  useEffect(() => {
    loadTopPerformers();
  }, [filters.customerId]);

  const loadTopPerformers = async () => {
    if (!filters.customerId) return;

    try {
      const response = await axios.get(`${API_BASE}/creative/top-performers`, {
        params: { customer_id: filters.customerId, limit: 10 },
      });
      setTopPerformers(response.data.top_performers || []);
    } catch (error) {
      console.error('Error loading top performers:', error);
    }
  };

  const handleGenerate = async () => {
    if (!filters.customerId) {
      enqueueSnackbar('Please select a customer first', { variant: 'warning' });
      return;
    }

    if (!generateForm.product || !generateForm.targetAudience) {
      enqueueSnackbar('Please fill in product and target audience', { variant: 'warning' });
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/creative/generate`, {
        customer_id: filters.customerId,
        campaign_goal: generateForm.campaignGoal,
        product: generateForm.product,
        target_audience: generateForm.targetAudience,
        tone: generateForm.tone,
        key_benefits: generateForm.keyBenefits.filter((b) => b.trim()),
        special_offer: generateForm.specialOffer || null,
      });

      setGeneratedAds(response.data.variations || []);
      enqueueSnackbar(`Generated ${response.data.variations?.length || 0} ad variations`, {
        variant: 'success',
      });
    } catch (error) {
      console.error('Error generating ads:', error);
      enqueueSnackbar('Failed to generate ad variations', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleOptimize = async () => {
    if (!filters.customerId) {
      enqueueSnackbar('Please select a customer first', { variant: 'warning' });
      return;
    }

    if (!optimizeForm.headline || !optimizeForm.description) {
      enqueueSnackbar('Please enter both headline and description', { variant: 'warning' });
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/creative/optimize`, {
        headline: optimizeForm.headline,
        description: optimizeForm.description,
        customer_id: filters.customerId,
      });

      setOptimizedAds(response.data);
      enqueueSnackbar('Ad optimized successfully!', { variant: 'success' });
    } catch (error) {
      console.error('Error optimizing ad:', error);
      enqueueSnackbar('Failed to optimize ad', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    enqueueSnackbar('Copied to clipboard!', { variant: 'success' });
  };

  const addBenefit = () => {
    setGenerateForm({ ...generateForm, keyBenefits: [...generateForm.keyBenefits, ''] });
  };

  const updateBenefit = (index: number, value: string) => {
    const newBenefits = [...generateForm.keyBenefits];
    newBenefits[index] = value;
    setGenerateForm({ ...generateForm, keyBenefits: newBenefits });
  };

  const removeBenefit = (index: number) => {
    const newBenefits = generateForm.keyBenefits.filter((_, i) => i !== index);
    setGenerateForm({ ...generateForm, keyBenefits: newBenefits });
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 600, mb: 1 }}>
            Creative Studio
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Generate and optimize ad copy with AI-powered insights
          </Typography>
        </Box>
        <AIBadge />
      </Box>

      {/* Mode Selector */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Stack direction="row" spacing={2}>
          <Button
            variant={mode === 'generate' ? 'contained' : 'outlined'}
            onClick={() => setMode('generate')}
            startIcon={<AutoFixHighIcon />}
            size="large"
          >
            Generate New Ads
          </Button>
          <Button
            variant={mode === 'optimize' ? 'contained' : 'outlined'}
            onClick={() => setMode('optimize')}
            startIcon={<TrendingUpIcon />}
            size="large"
          >
            Optimize Existing Ad
          </Button>
        </Stack>
      </Paper>

      <Grid container spacing={3}>
        {/* Left Column - Input Form */}
        <Grid item xs={12} md={4}>
          <GradientCard variant="ai" intensity="subtle">
            <CardContent>
              {mode === 'generate' ? (
                <>
                  <Typography variant="h6" sx={{ mb: 3 }}>
                    Ad Generation Settings
                  </Typography>

                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel>Campaign Goal</InputLabel>
                    <Select
                      value={generateForm.campaignGoal}
                      onChange={(e) => setGenerateForm({ ...generateForm, campaignGoal: e.target.value })}
                      label="Campaign Goal"
                    >
                      <MenuItem value="sales">Sales</MenuItem>
                      <MenuItem value="awareness">Brand Awareness</MenuItem>
                      <MenuItem value="leads">Lead Generation</MenuItem>
                      <MenuItem value="event">Event Promotion</MenuItem>
                    </Select>
                  </FormControl>

                  <TextField
                    fullWidth
                    label="Product/Service"
                    value={generateForm.product}
                    onChange={(e) => setGenerateForm({ ...generateForm, product: e.target.value })}
                    sx={{ mb: 2 }}
                    required
                  />

                  <TextField
                    fullWidth
                    label="Target Audience"
                    value={generateForm.targetAudience}
                    onChange={(e) => setGenerateForm({ ...generateForm, targetAudience: e.target.value })}
                    placeholder="e.g., Small business owners, 25-45 years old"
                    sx={{ mb: 2 }}
                    required
                  />

                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel>Tone</InputLabel>
                    <Select
                      value={generateForm.tone}
                      onChange={(e) => setGenerateForm({ ...generateForm, tone: e.target.value })}
                      label="Tone"
                    >
                      <MenuItem value="professional">Professional</MenuItem>
                      <MenuItem value="casual">Casual</MenuItem>
                      <MenuItem value="urgent">Urgent</MenuItem>
                      <MenuItem value="friendly">Friendly</MenuItem>
                    </Select>
                  </FormControl>

                  <Typography variant="subtitle2" sx={{ mb: 1 }}>
                    Key Benefits
                  </Typography>
                  {generateForm.keyBenefits.map((benefit, index) => (
                    <Box key={index} sx={{ display: 'flex', gap: 1, mb: 1 }}>
                      <TextField
                        fullWidth
                        size="small"
                        value={benefit}
                        onChange={(e) => updateBenefit(index, e.target.value)}
                        placeholder="e.g., Free shipping"
                      />
                      {generateForm.keyBenefits.length > 1 && (
                        <IconButton size="small" onClick={() => removeBenefit(index)}>
                          ×
                        </IconButton>
                      )}
                    </Box>
                  ))}
                  <Button size="small" onClick={addBenefit} sx={{ mb: 2 }}>
                    + Add Benefit
                  </Button>

                  <TextField
                    fullWidth
                    label="Special Offer (Optional)"
                    value={generateForm.specialOffer}
                    onChange={(e) => setGenerateForm({ ...generateForm, specialOffer: e.target.value })}
                    placeholder="e.g., 30% off this weekend"
                    sx={{ mb: 3 }}
                  />

                  <Button
                    fullWidth
                    variant="contained"
                    size="large"
                    onClick={handleGenerate}
                    disabled={loading}
                    startIcon={<AutoFixHighIcon />}
                  >
                    Generate Ad Variations
                  </Button>
                </>
              ) : (
                <>
                  <Typography variant="h6" sx={{ mb: 3 }}>
                    Optimize Your Ad
                  </Typography>

                  <TextField
                    fullWidth
                    label="Current Headline"
                    value={optimizeForm.headline}
                    onChange={(e) => setOptimizeForm({ ...optimizeForm, headline: e.target.value })}
                    placeholder="Enter your current ad headline"
                    sx={{ mb: 2 }}
                    required
                  />

                  <TextField
                    fullWidth
                    label="Current Description"
                    value={optimizeForm.description}
                    onChange={(e) => setOptimizeForm({ ...optimizeForm, description: e.target.value })}
                    placeholder="Enter your current ad description"
                    multiline
                    rows={4}
                    sx={{ mb: 3 }}
                    required
                  />

                  <Button
                    fullWidth
                    variant="contained"
                    size="large"
                    onClick={handleOptimize}
                    disabled={loading}
                    startIcon={<TrendingUpIcon />}
                  >
                    Optimize Ad Copy
                  </Button>

                  {optimizedAds && (
                    <Box sx={{ mt: 3 }}>
                      <Divider sx={{ my: 2 }} />
                      <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                        Current Score
                      </Typography>
                      <ConfidenceScore value={optimizedAds.analysis.current_score * 10} label="Ad Quality" />

                      {optimizedAds.analysis.issues.length > 0 && (
                        <Alert severity="warning" sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                            Issues Found:
                          </Typography>
                          <ul style={{ margin: 0, paddingLeft: 20 }}>
                            {optimizedAds.analysis.issues.map((issue: string, i: number) => (
                              <li key={i}>{issue}</li>
                            ))}
                          </ul>
                        </Alert>
                      )}

                      {optimizedAds.analysis.suggestions.length > 0 && (
                        <Alert severity="info" sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                            Suggestions:
                          </Typography>
                          <ul style={{ margin: 0, paddingLeft: 20 }}>
                            {optimizedAds.analysis.suggestions.map((suggestion: string, i: number) => (
                              <li key={i}>{suggestion}</li>
                            ))}
                          </ul>
                        </Alert>
                      )}
                    </Box>
                  )}
                </>
              )}
            </CardContent>
          </GradientCard>

          {/* Top Performers */}
          {topPerformers.length > 0 && (
            <Card sx={{ mt: 3 }}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Top Performing Keywords
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Use these in your ad copy for better relevance
                </Typography>
                <Stack direction="row" flexWrap="wrap" gap={1}>
                  {topPerformers.slice(0, 10).map((kw, index) => (
                    <Chip
                      key={index}
                      label={kw.keyword}
                      size="small"
                      icon={<TrendingUpIcon />}
                      onClick={() => copyToClipboard(kw.keyword)}
                      sx={{ cursor: 'pointer' }}
                    />
                  ))}
                </Stack>
              </CardContent>
            </Card>
          )}
        </Grid>

        {/* Right Column - Results */}
        <Grid item xs={12} md={8}>
          {loading ? (
            <AILoadingState message="AI is creating your ad variations..." size="large" variant="pulse" />
          ) : mode === 'generate' && generatedAds.length > 0 ? (
            <Box>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Generated Ad Variations ({generatedAds.length})
              </Typography>
              <Grid container spacing={2}>
                {generatedAds.map((ad) => (
                  <Grid item xs={12} md={6} key={ad.id}>
                    <Card
                      sx={{
                        border: `2px solid ${colors.primary.main}`,
                        transition: 'all 0.3s',
                        '&:hover': {
                          transform: 'translateY(-4px)',
                          boxShadow: shadows.lg,
                        },
                      }}
                    >
                      <CardContent>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                          <Chip
                            label={`Score: ${ad.score}/10`}
                            color={ad.score >= 8.5 ? 'success' : ad.score >= 7.5 ? 'info' : 'warning'}
                            size="small"
                          />
                          <Chip label={ad.predicted_ctr} size="small" icon={<TrendingUpIcon />} />
                        </Box>

                        <Typography variant="h6" sx={{ mb: 1, color: colors.primary.main }}>
                          {ad.headline}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                          {ad.description}
                        </Typography>

                        <Divider sx={{ my: 2 }} />

                        <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                          Strengths:
                        </Typography>
                        <Stack direction="row" flexWrap="wrap" gap={0.5} sx={{ mb: 2 }}>
                          {ad.strengths.map((strength: string, i: number) => (
                            <Chip key={i} label={strength} size="small" variant="outlined" />
                          ))}
                        </Stack>

                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <IconButton
                            size="small"
                            onClick={() => copyToClipboard(`${ad.headline}\n${ad.description}`)}
                            color="primary"
                          >
                            <ContentCopyIcon fontSize="small" />
                          </IconButton>
                          <Chip label={ad.policy_status} size="small" icon={<VerifiedIcon />} color="success" />
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
          ) : mode === 'optimize' && optimizedAds ? (
            <Box>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Optimized Versions
              </Typography>

              {/* Comparison */}
              <GradientCard variant="success" intensity="subtle" sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                    Before vs After Comparison
                  </Typography>
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                      <Typography variant="caption" color="text.secondary">
                        Original (Score: {optimizedAds.comparison.original.score}/10)
                      </Typography>
                      <Typography variant="h6" sx={{ mt: 1, mb: 1 }}>
                        {optimizedAds.comparison.original.headline}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {optimizedAds.comparison.original.description}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="caption" color="success.main">
                        Best Optimized (Score: {optimizedAds.comparison.best_optimized.score}/10)
                      </Typography>
                      <Typography variant="h6" sx={{ mt: 1, mb: 1, color: colors.success.main }}>
                        {optimizedAds.comparison.best_optimized.headline}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {optimizedAds.comparison.best_optimized.description}
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </GradientCard>

              {/* All Optimized Versions */}
              <Grid container spacing={2}>
                {optimizedAds.optimized_versions.map((version: any) => (
                  <Grid item xs={12} md={6} key={version.version}>
                    <Card
                      sx={{
                        border: `2px solid ${colors.success.main}`,
                        transition: 'all 0.3s',
                        '&:hover': {
                          transform: 'translateY(-4px)',
                          boxShadow: shadows.lg,
                        },
                      }}
                    >
                      <CardContent>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                          <Chip label={`Version ${version.version}`} size="small" />
                          <Chip
                            label={`Score: ${version.score}/10`}
                            color={version.score >= 8.5 ? 'success' : 'info'}
                            size="small"
                          />
                        </Box>

                        <Typography variant="h6" sx={{ mb: 1, color: colors.success.main }}>
                          {version.headline}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                          {version.description}
                        </Typography>

                        <Divider sx={{ my: 2 }} />

                        <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                          Improvements:
                        </Typography>
                        <Stack direction="row" flexWrap="wrap" gap={0.5} sx={{ mb: 2 }}>
                          {version.improvements.map((improvement: string, i: number) => (
                            <Chip key={i} label={improvement} size="small" variant="outlined" color="success" />
                          ))}
                        </Stack>

                        <IconButton
                          size="small"
                          onClick={() => copyToClipboard(`${version.headline}\n${version.description}`)}
                          color="primary"
                        >
                          <ContentCopyIcon fontSize="small" />
                        </IconButton>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
          ) : (
            <EmptyState
              icon="ai"
              title={mode === 'generate' ? 'Generate Your First Ad' : 'Optimize Your Ad Copy'}
              description={
                mode === 'generate'
                  ? 'Fill in the form on the left and click "Generate Ad Variations" to create AI-powered ad copy.'
                  : 'Enter your existing ad copy on the left and get AI-powered optimization suggestions.'
              }
            />
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default CreativeStudioPage;
