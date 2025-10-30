/**
 * Decision Intelligence Modal - Compact Tabbed Version with Animations
 * Shows success, failure, and no-action scenarios in tabs
 * Compact, focused design with smooth animations
 */
import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  Box,
  Typography,
  IconButton,
  Button,
  Chip,
  Alert,
  Divider,
  useTheme,
  Tabs,
  Tab,
  Grid,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Fade,
  Grow,
  Slide,
  Zoom,
} from '@mui/material';
import {
  Close,
  Psychology,
  CheckCircle,
  Warning,
  Error as ErrorIcon,
  TrendingUp,
  TrendingDown,
  Timeline,
  ExpandMore,
  PlayArrow,
  Lightbulb,
} from '@mui/icons-material';
import { generateKeywordSimulation, SimulationResult } from '../../utils/scenario-calculator';
import { formatCurrency } from '../charts/PowerBITheme';

interface DecisionIntelligenceProps {
  open: boolean;
  onClose: () => void;
  keywordData?: any;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel = (props: TabPanelProps) => {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`scenario-tabpanel-${index}`}
      aria-labelledby={`scenario-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Fade in={value === index} timeout={600}>
          <Box sx={{ pt: 3 }}>{children}</Box>
        </Fade>
      )}
    </div>
  );
};

const DecisionIntelligence: React.FC<DecisionIntelligenceProps> = ({
  open,
  onClose,
  keywordData,
}) => {
  const theme = useTheme();
  const [selectedTab, setSelectedTab] = useState(0);
  const [selectedKeyword, setSelectedKeyword] = useState<number>(0);
  const [simulation, setSimulation] = useState<SimulationResult | null>(null);

  React.useEffect(() => {
    if (keywordData && keywordData.keywords && keywordData.keywords.length > 0) {
      const keyword = keywordData.keywords[selectedKeyword];
      const sim = generateKeywordSimulation({
        keyword_text: keyword.keyword_text,
        ad_clicks: keyword.ad_clicks,
        ad_cost: keyword.ad_cost,
        ad_ctr: keyword.ad_ctr,
        ad_conversions: keyword.ad_conversions,
        ga4_bounce_rate: keyword.ga4_bounce_rate,
        ga4_engagement_rate: keyword.ga4_engagement_rate,
        ga4_avg_session_duration: keyword.ga4_avg_session_duration,
        quality_score: keyword.quality_score,
      });
      setSimulation(sim);
    }
  }, [keywordData, selectedKeyword]);

  if (!simulation) {
    return null;
  }

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  const scenarios = [
    { data: simulation.scenarios.success, type: 'success', label: 'Success', icon: <CheckCircle /> },
    { data: simulation.scenarios.failure, type: 'failure', label: 'Failure', icon: <Warning /> },
    { data: simulation.scenarios.noAction, type: 'noAction', label: 'No Action', icon: <ErrorIcon /> },
  ];

  const currentScenario = scenarios[selectedTab].data;

  const getTabColor = (index: number) => {
    if (index === 0) return theme.palette.success.main;
    if (index === 1) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      TransitionComponent={Slide}
      TransitionProps={{ direction: 'up' } as any}
      PaperProps={{
        sx: {
          bgcolor: 'background.paper',
          borderRadius: 2,
          boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
        },
      }}
    >
      {/* Header */}
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Zoom in={open} timeout={500}>
              <Box
                sx={{
                  animation: 'pulse 2s ease-in-out infinite',
                  '@keyframes pulse': {
                    '0%, 100%': { transform: 'scale(1)' },
                    '50%': { transform: 'scale(1.05)' },
                  },
                }}
              >
                <Psychology color="primary" sx={{ fontSize: 32 }} />
              </Box>
            </Zoom>
            <Fade in={open} timeout={800}>
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  Decision Intelligence
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Analyzing: {simulation.keyword}
                </Typography>
              </Box>
            </Fade>
          </Box>
          <Fade in={open} timeout={600}>
            <IconButton onClick={onClose} size="small">
              <Close />
            </IconButton>
          </Fade>
        </Box>
      </DialogTitle>

      <Divider />

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', px: 3 }}>
        <Tabs
          value={selectedTab}
          onChange={handleTabChange}
          variant="fullWidth"
          sx={{
            '& .MuiTab-root': {
              minHeight: 64,
              textTransform: 'none',
              fontWeight: 600,
              transition: 'all 0.3s ease',
            },
            '& .Mui-selected': {
              color: getTabColor(selectedTab),
            },
            '& .MuiTabs-indicator': {
              backgroundColor: getTabColor(selectedTab),
              height: 3,
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            },
          }}
        >
          {scenarios.map((scenario, index) => (
            <Tab
              key={index}
              icon={scenario.icon}
              label={scenario.label}
              iconPosition="start"
              sx={{
                '&.Mui-selected': {
                  bgcolor: `${getTabColor(index)}10`,
                  transform: 'scale(1.02)',
                },
                '&:hover': {
                  bgcolor: `${getTabColor(index)}08`,
                  transform: 'translateY(-2px)',
                },
              }}
            />
          ))}
        </Tabs>
      </Box>

      <DialogContent sx={{ px: 3, pb: 3 }}>
        {/* AI Recommendation - Compact */}
        {selectedTab === 0 && (
          <Slide in={selectedTab === 0} direction="down" timeout={500}>
            <Alert
              severity="info"
              icon={<Lightbulb />}
              sx={{
                mb: 2,
                borderLeft: `4px solid ${theme.palette.primary.main}`,
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateX(4px)',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
                },
              }}
            >
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                {simulation.recommendation.action}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {simulation.recommendation.rationale}
              </Typography>
            </Alert>
          </Slide>
        )}

        {/* Tab Panels */}
        {scenarios.map((scenario, index) => (
          <TabPanel key={index} value={selectedTab} index={index}>
            {/* Scenario Header */}
            <Box sx={{ mb: 2 }}>
              <Fade in timeout={300}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
                  <Typography
                    variant="h6"
                    sx={{
                      fontWeight: 700,
                      color: getTabColor(index),
                      transition: 'all 0.3s ease',
                    }}
                  >
                    {scenario.data.name}
                  </Typography>
                  <Zoom in timeout={500}>
                    <Chip
                      label={`${scenario.data.probability}% probability`}
                      size="small"
                      sx={{
                        bgcolor: getTabColor(index),
                        color: 'white',
                        fontWeight: 600,
                        transition: 'all 0.3s ease',
                        animation: 'pulse 3s ease-in-out infinite',
                        '@keyframes pulse': {
                          '0%, 100%': { transform: 'scale(1)', opacity: 1 },
                          '50%': { transform: 'scale(1.05)', opacity: 0.9 },
                        },
                        '&:hover': {
                          transform: 'scale(1.1)',
                          boxShadow: `0 4px 12px ${getTabColor(index)}`,
                        },
                      }}
                    />
                  </Zoom>
                </Box>
              </Fade>
              <Fade in timeout={400}>
                <Typography variant="body2" color="text.secondary">
                  {scenario.data.description}
                </Typography>
              </Fade>
            </Box>

            {/* Key Metrics - Compact 2x2 Grid */}
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={6}>
                <Grow in timeout={400}>
                  <Box
                    sx={{
                      p: 2,
                      borderRadius: 1,
                      border: `1px solid ${theme.palette.divider}`,
                      bgcolor: 'background.default',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                        borderColor: theme.palette.primary.main,
                      },
                    }}
                  >
                    <Typography variant="caption" color="text.secondary" gutterBottom display="block">
                      CTR Change
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      {scenario.data.metrics.ctrChange > 0 ? (
                        <TrendingUp fontSize="small" color="success" />
                      ) : (
                        <TrendingDown fontSize="small" color="error" />
                      )}
                      <Typography variant="h5" sx={{ fontWeight: 700 }}>
                        {scenario.data.metrics.ctrChange > 0 ? '+' : ''}
                        {scenario.data.metrics.ctrChange.toFixed(0)}%
                      </Typography>
                    </Box>
                  </Box>
                </Grow>
              </Grid>

              <Grid item xs={6}>
                <Grow in timeout={600}>
                  <Box
                    sx={{
                      p: 2,
                      borderRadius: 1,
                      border: `1px solid ${theme.palette.divider}`,
                      bgcolor: 'background.default',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                        borderColor: theme.palette.primary.main,
                      },
                    }}
                  >
                    <Typography variant="caption" color="text.secondary" gutterBottom display="block">
                      CPC Change
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      {scenario.data.metrics.cpcChange < 0 ? (
                        <TrendingDown fontSize="small" color="success" />
                      ) : (
                        <TrendingUp fontSize="small" color="error" />
                      )}
                      <Typography variant="h5" sx={{ fontWeight: 700 }}>
                        {scenario.data.metrics.cpcChange > 0 ? '+' : ''}
                        {scenario.data.metrics.cpcChange.toFixed(0)}%
                      </Typography>
                    </Box>
                  </Box>
                </Grow>
              </Grid>

              <Grid item xs={6}>
                <Grow in timeout={800}>
                  <Box
                    sx={{
                      p: 2,
                      borderRadius: 1,
                      border: `1px solid ${theme.palette.divider}`,
                      bgcolor: 'background.default',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                        borderColor: theme.palette.primary.main,
                      },
                    }}
                  >
                    <Typography variant="caption" color="text.secondary" gutterBottom display="block">
                      Conversions
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      {scenario.data.metrics.conversionsChange > 0 ? (
                        <TrendingUp fontSize="small" color="success" />
                      ) : (
                        <TrendingDown fontSize="small" color="error" />
                      )}
                      <Typography variant="h5" sx={{ fontWeight: 700 }}>
                        {scenario.data.metrics.conversionsChange > 0 ? '+' : ''}
                        {scenario.data.metrics.conversionsChange.toFixed(0)}%
                      </Typography>
                    </Box>
                  </Box>
                </Grow>
              </Grid>

              <Grid item xs={6}>
                <Grow in timeout={1000}>
                  <Box
                    sx={{
                      p: 2,
                      borderRadius: 1,
                      border: `1px solid ${theme.palette.divider}`,
                      bgcolor: 'background.default',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                        borderColor: theme.palette.primary.main,
                      },
                    }}
                  >
                    <Typography variant="caption" color="text.secondary" gutterBottom display="block">
                      Monthly ROI
                    </Typography>
                    <Typography
                      variant="h5"
                      sx={{
                        fontWeight: 700,
                        color: scenario.data.metrics.monthlyROI > 0 ? 'success.main' : 'error.main',
                        mt: 0.5,
                      }}
                    >
                      {formatCurrency(scenario.data.metrics.monthlyROI)}
                    </Typography>
                  </Box>
                </Grow>
              </Grid>
            </Grid>

            {/* Timeline */}
            <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
              <Timeline fontSize="small" color="action" />
              <Typography variant="body2">
                <strong>Timeline:</strong> {scenario.data.timeline}
              </Typography>
            </Box>

            {/* Expandable Details */}
            <Accordion
              sx={{
                boxShadow: 'none',
                border: `1px solid ${theme.palette.divider}`,
                '&:before': { display: 'none' },
              }}
            >
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  View Detailed Analysis
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                {/* Risks */}
                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                  ⚠️ Risks:
                </Typography>
                <List dense>
                  {scenario.data.risks.map((risk: string, idx: number) => (
                    <ListItem key={idx} sx={{ py: 0.5, pl: 0 }}>
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        <Warning fontSize="small" color="warning" />
                      </ListItemIcon>
                      <ListItemText
                        primary={risk}
                        primaryTypographyProps={{ variant: 'caption' }}
                      />
                    </ListItem>
                  ))}
                </List>

                {/* Opportunities */}
                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, mt: 2 }}>
                  💡 Opportunities:
                </Typography>
                <List dense>
                  {scenario.data.opportunities.map((opp: string, idx: number) => (
                    <ListItem key={idx} sx={{ py: 0.5, pl: 0 }}>
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        <Lightbulb fontSize="small" color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={opp}
                        primaryTypographyProps={{ variant: 'caption' }}
                      />
                    </ListItem>
                  ))}
                </List>

                {/* Action Steps */}
                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, mt: 2 }}>
                  📋 Action Steps:
                </Typography>
                <List dense>
                  {scenario.data.actionSteps.map((step: string, idx: number) => (
                    <ListItem key={idx} sx={{ py: 0.5, pl: 0 }}>
                      <ListItemText
                        primary={`${idx + 1}. ${step}`}
                        primaryTypographyProps={{ variant: 'caption' }}
                      />
                    </ListItem>
                  ))}
                </List>
              </AccordionDetails>
            </Accordion>
          </TabPanel>
        ))}

        {/* Action Buttons */}
        <Box sx={{ display: 'flex', gap: 2, mt: 3, justifyContent: 'flex-end' }}>
          <Fade in timeout={800}>
            <Button
              variant="outlined"
              onClick={onClose}
              sx={{
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'scale(1.05)',
                },
              }}
            >
              Close
            </Button>
          </Fade>
          {selectedTab === 0 && (
            <Zoom in timeout={1000}>
              <Button
                variant="contained"
                startIcon={<PlayArrow />}
                sx={{
                  background: `linear-gradient(45deg, ${theme.palette.primary.main} 30%, ${theme.palette.secondary.main} 90%)`,
                  transition: 'all 0.3s ease',
                  animation: 'glow 2s ease-in-out infinite',
                  '@keyframes glow': {
                    '0%, 100%': {
                      boxShadow: `0 0 10px ${theme.palette.primary.main}`,
                    },
                    '50%': {
                      boxShadow: `0 0 20px ${theme.palette.primary.main}, 0 0 30px ${theme.palette.secondary.main}`,
                    },
                  },
                  '&:hover': {
                    transform: 'scale(1.08)',
                    boxShadow: `0 8px 24px ${theme.palette.primary.main}`,
                  },
                }}
              >
                Implement
              </Button>
            </Zoom>
          )}
        </Box>
      </DialogContent>
    </Dialog>
  );
};

export default DecisionIntelligence;
