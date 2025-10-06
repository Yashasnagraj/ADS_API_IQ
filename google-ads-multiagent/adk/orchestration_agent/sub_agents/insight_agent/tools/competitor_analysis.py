"""
Competitor analysis tools for Insight Agent
"""
from typing import Dict, List, Any, Optional, Tuple
from langchain.tools import Tool
from loguru import logger
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class CompetitorAnalysis:
    """Analyzes competitive landscape and auction insights"""

    def __init__(self):
        logger.info("Competitor Analysis initialized")

    def analyze_auction_insights(
        self,
        auction_data: List[Dict[str, Any]],
        competitor_domains: List[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze Google Ads Auction Insights data

        Args:
            auction_data: Auction insights data from Google Ads
            competitor_domains: List of competitor domains to focus on

        Returns:
            Competitive analysis with insights and recommendations
        """
        try:
            if not auction_data:
                return {"error": "No auction data provided"}

            df = pd.DataFrame(auction_data)

            analysis = {
                'summary': {},
                'competitor_metrics': {},
                'competitive_position': {},
                'opportunities': [],
                'threats': [],
                'recommendations': []
            }

            # Overall competitive metrics
            if 'impression_share' in df.columns:
                our_impression_share = df[df.get('is_you', False)]['impression_share'].iloc[0] if any(df.get('is_you', False)) else 0
            else:
                our_impression_share = 0

            analysis['summary'] = {
                'total_competitors': len(df) - 1 if 'is_you' in df.columns else len(df),
                'our_impression_share': round(our_impression_share * 100, 2),
                'market_concentration': self._calculate_market_concentration(df),
                'competitive_intensity': self._calculate_competitive_intensity(df)
            }

            # Analyze each competitor
            competitors = df[~df.get('is_you', False)] if 'is_you' in df.columns else df

            for _, competitor in competitors.iterrows():
                domain = competitor.get('domain', 'unknown')

                # Skip if not in focus list
                if competitor_domains and domain not in competitor_domains:
                    continue

                metrics = {
                    'domain': domain,
                    'impression_share': round(competitor.get('impression_share', 0) * 100, 2),
                    'overlap_rate': round(competitor.get('overlap_rate', 0) * 100, 2),
                    'position_above_rate': round(competitor.get('position_above_rate', 0) * 100, 2),
                    'top_of_page_rate': round(competitor.get('top_of_page_rate', 0) * 100, 2),
                    'absolute_top_rate': round(competitor.get('abs_top_of_page_rate', 0) * 100, 2),
                    'outranking_share': round(competitor.get('outranking_share', 0) * 100, 2)
                }

                # Competitive strength score
                metrics['competitive_strength'] = self._calculate_competitor_strength(metrics)

                # Classify competitor
                metrics['classification'] = self._classify_competitor(metrics)

                analysis['competitor_metrics'][domain] = metrics

                # Identify threats
                if metrics['position_above_rate'] > 60:
                    analysis['threats'].append({
                        'competitor': domain,
                        'type': 'dominant_position',
                        'severity': 'high',
                        'description': f"{domain} appears above you {metrics['position_above_rate']:.1f}% of the time"
                    })

                # Identify opportunities
                if metrics['overlap_rate'] > 50 and metrics['outranking_share'] < 30:
                    analysis['opportunities'].append({
                        'competitor': domain,
                        'type': 'improve_outranking',
                        'potential': 'high',
                        'description': f"High overlap with {domain} but low outranking share"
                    })

            # Competitive positioning
            analysis['competitive_position'] = self._determine_competitive_position(
                our_impression_share,
                analysis['competitor_metrics']
            )

            # Generate recommendations
            analysis['recommendations'] = self._generate_competitive_recommendations(analysis)

            # Competitive gaps
            analysis['competitive_gaps'] = self._identify_competitive_gaps(df)

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing auction insights: {e}")
            return {"error": str(e)}

    def analyze_competitive_keywords(
        self,
        keyword_data: List[Dict[str, Any]],
        competitor_data: Optional[Dict[str, List[str]]] = None
    ) -> Dict[str, Any]:
        """
        Analyze competitive keyword landscape

        Args:
            keyword_data: Your keyword performance data
            competitor_data: Competitor keyword data (if available)

        Returns:
            Competitive keyword analysis
        """
        try:
            if not keyword_data:
                return {"error": "No keyword data provided"}

            df = pd.DataFrame(keyword_data)

            analysis = {
                'keyword_competition': {},
                'high_competition_keywords': [],
                'low_competition_opportunities': [],
                'keyword_gaps': [],
                'bidding_opportunities': []
            }

            # Analyze competition level for each keyword
            for _, row in df.iterrows():
                keyword = row.get('keyword_text', '')
                competition_level = row.get('competition', 'MEDIUM')
                avg_cpc = row.get('avg_cpc', 0)

                keyword_analysis = {
                    'keyword': keyword,
                    'competition_level': competition_level,
                    'avg_cpc': avg_cpc,
                    'search_volume': row.get('search_volume', 0),
                    'our_avg_position': row.get('avg_position', 0),
                    'our_impression_share': row.get('search_impression_share', 0)
                }

                # Calculate competition score
                keyword_analysis['competition_score'] = self._calculate_keyword_competition_score(row)

                # Identify opportunities
                if competition_level == 'LOW' and row.get('search_volume', 0) > 1000:
                    analysis['low_competition_opportunities'].append({
                        'keyword': keyword,
                        'search_volume': row.get('search_volume', 0),
                        'avg_cpc': avg_cpc,
                        'opportunity_score': self._calculate_opportunity_score(row)
                    })

                # High competition keywords
                if competition_level == 'HIGH':
                    analysis['high_competition_keywords'].append({
                        'keyword': keyword,
                        'avg_cpc': avg_cpc,
                        'our_position': row.get('avg_position', 0),
                        'strategy': self._suggest_competition_strategy(row)
                    })

                # Bidding opportunities
                if row.get('first_page_bid', 0) > 0:
                    current_bid = row.get('max_cpc', 0)
                    first_page_bid = row['first_page_bid']

                    if current_bid < first_page_bid * 0.8:
                        analysis['bidding_opportunities'].append({
                            'keyword': keyword,
                            'current_bid': current_bid,
                            'recommended_bid': first_page_bid,
                            'potential_improvement': 'Reach first page'
                        })

                analysis['keyword_competition'][keyword] = keyword_analysis

            # Analyze competitor keywords if available
            if competitor_data:
                analysis['keyword_gaps'] = self._identify_keyword_gaps(
                    set(df['keyword_text'].unique()),
                    competitor_data
                )

            # Sort opportunities by score
            analysis['low_competition_opportunities'] = sorted(
                analysis['low_competition_opportunities'],
                key=lambda x: x['opportunity_score'],
                reverse=True
            )[:20]

            # Summary statistics
            analysis['summary'] = {
                'total_keywords': len(df),
                'high_competition_count': len(analysis['high_competition_keywords']),
                'opportunities_found': len(analysis['low_competition_opportunities']),
                'avg_competition_score': np.mean([
                    kw['competition_score']
                    for kw in analysis['keyword_competition'].values()
                ])
            }

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing competitive keywords: {e}")
            return {"error": str(e)}

    def analyze_share_of_voice(
        self,
        impression_data: List[Dict[str, Any]],
        market_size_estimate: float = None
    ) -> Dict[str, Any]:
        """
        Analyze share of voice in the market

        Args:
            impression_data: Impression share data
            market_size_estimate: Estimated total market impressions

        Returns:
            Share of voice analysis
        """
        try:
            if not impression_data:
                return {"error": "No impression data provided"}

            df = pd.DataFrame(impression_data)

            analysis = {
                'current_sov': {},
                'sov_trend': {},
                'lost_sov_analysis': {},
                'sov_opportunities': [],
                'competitive_comparison': {}
            }

            # Current share of voice
            if 'impression_share' in df.columns:
                latest_data = df.iloc[-1] if not df.empty else {}

                analysis['current_sov'] = {
                    'search_impression_share': round(latest_data.get('search_impression_share', 0) * 100, 2),
                    'search_exact_match_is': round(latest_data.get('search_exact_match_impression_share', 0) * 100, 2),
                    'display_impression_share': round(latest_data.get('content_impression_share', 0) * 100, 2)
                }

            # Lost share of voice analysis
            analysis['lost_sov_analysis'] = {
                'lost_to_budget': {
                    'search': round(latest_data.get('search_lost_impression_share_budget', 0) * 100, 2),
                    'display': round(latest_data.get('content_lost_impression_share_budget', 0) * 100, 2),
                    'impact': self._calculate_lost_sov_impact(latest_data, 'budget')
                },
                'lost_to_rank': {
                    'search': round(latest_data.get('search_lost_impression_share_rank', 0) * 100, 2),
                    'display': round(latest_data.get('content_lost_impression_share_rank', 0) * 100, 2),
                    'impact': self._calculate_lost_sov_impact(latest_data, 'rank')
                }
            }

            # SOV trend analysis
            if len(df) > 1:
                analysis['sov_trend'] = self._analyze_sov_trend(df)

            # Identify SOV opportunities
            total_lost = (
                analysis['lost_sov_analysis']['lost_to_budget']['search'] +
                analysis['lost_sov_analysis']['lost_to_rank']['search']
            )

            if analysis['lost_sov_analysis']['lost_to_budget']['search'] > 10:
                analysis['sov_opportunities'].append({
                    'type': 'budget_increase',
                    'potential_gain': f"{analysis['lost_sov_analysis']['lost_to_budget']['search']:.1f}%",
                    'priority': 'high' if analysis['lost_sov_analysis']['lost_to_budget']['search'] > 20 else 'medium',
                    'recommendation': 'Increase campaign budgets to capture lost impressions'
                })

            if analysis['lost_sov_analysis']['lost_to_rank']['search'] > 15:
                analysis['sov_opportunities'].append({
                    'type': 'quality_improvement',
                    'potential_gain': f"{analysis['lost_sov_analysis']['lost_to_rank']['search']:.1f}%",
                    'priority': 'high',
                    'recommendation': 'Improve Quality Score and increase bids'
                })

            # Market share estimation
            if market_size_estimate:
                our_impressions = latest_data.get('impressions', 0)
                analysis['market_share_estimate'] = {
                    'our_impressions': our_impressions,
                    'market_size': market_size_estimate,
                    'estimated_share': round((our_impressions / market_size_estimate * 100), 2),
                    'growth_potential': round((market_size_estimate - our_impressions) / our_impressions * 100, 2)
                }

            # Competitive benchmarking
            analysis['competitive_comparison'] = self._benchmark_sov(analysis['current_sov'])

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing share of voice: {e}")
            return {"error": str(e)}

    def analyze_competitive_positioning(
        self,
        performance_data: Dict[str, Any],
        competitor_benchmarks: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze competitive positioning and market standing

        Args:
            performance_data: Your performance metrics
            competitor_benchmarks: Industry or competitor benchmarks

        Returns:
            Competitive positioning analysis
        """
        try:
            analysis = {
                'positioning_score': 0,
                'strengths': [],
                'weaknesses': [],
                'competitive_advantages': [],
                'improvement_areas': [],
                'strategic_recommendations': []
            }

            # Default benchmarks if not provided
            if not competitor_benchmarks:
                competitor_benchmarks = {
                    'avg_ctr': 3.17,  # Google Ads average
                    'avg_conversion_rate': 3.75,
                    'avg_cpc': 2.69,
                    'avg_position': 2.5,
                    'avg_quality_score': 5.5
                }

            # Compare metrics
            comparisons = {}

            for metric, benchmark in competitor_benchmarks.items():
                our_value = performance_data.get(metric, 0)

                if benchmark > 0:
                    performance_ratio = (our_value / benchmark - 1) * 100
                else:
                    performance_ratio = 0

                comparisons[metric] = {
                    'our_value': our_value,
                    'benchmark': benchmark,
                    'performance': performance_ratio,
                    'status': self._classify_performance(metric, performance_ratio)
                }

                # Identify strengths and weaknesses
                if performance_ratio > 20:
                    analysis['strengths'].append({
                        'metric': metric,
                        'advantage': f"{performance_ratio:.1f}% better than benchmark",
                        'value': our_value
                    })
                elif performance_ratio < -20:
                    analysis['weaknesses'].append({
                        'metric': metric,
                        'gap': f"{abs(performance_ratio):.1f}% below benchmark",
                        'value': our_value,
                        'target': benchmark
                    })

            # Calculate positioning score (0-100)
            analysis['positioning_score'] = self._calculate_positioning_score(comparisons)

            # Identify competitive advantages
            if 'avg_quality_score' in performance_data:
                if performance_data['avg_quality_score'] >= 7:
                    analysis['competitive_advantages'].append({
                        'advantage': 'High Quality Score',
                        'impact': 'Lower CPCs and better ad positions',
                        'score': performance_data['avg_quality_score']
                    })

            if 'conversion_rate' in performance_data:
                if performance_data['conversion_rate'] > competitor_benchmarks.get('avg_conversion_rate', 0) * 1.5:
                    analysis['competitive_advantages'].append({
                        'advantage': 'Superior Conversion Rate',
                        'impact': 'More efficient spend and higher ROI',
                        'rate': f"{performance_data['conversion_rate']:.2f}%"
                    })

            # Improvement areas
            for weakness in analysis['weaknesses']:
                metric = weakness['metric']
                improvement = {
                    'area': metric,
                    'current': weakness['value'],
                    'target': weakness['target'],
                    'priority': 'high' if weakness['gap'].split('%')[0] > '30' else 'medium'
                }

                if metric == 'avg_ctr':
                    improvement['actions'] = [
                        'Improve ad copy relevance',
                        'Test new ad formats',
                        'Refine keyword targeting'
                    ]
                elif metric == 'avg_conversion_rate':
                    improvement['actions'] = [
                        'Optimize landing pages',
                        'Improve audience targeting',
                        'Test conversion-focused ad copy'
                    ]
                elif metric == 'avg_quality_score':
                    improvement['actions'] = [
                        'Improve keyword relevance',
                        'Enhance landing page experience',
                        'Increase CTR through better ads'
                    ]

                analysis['improvement_areas'].append(improvement)

            # Strategic recommendations
            analysis['strategic_recommendations'] = self._generate_positioning_recommendations(
                analysis,
                comparisons
            )

            analysis['market_position'] = self._determine_market_position(
                analysis['positioning_score']
            )

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing competitive positioning: {e}")
            return {"error": str(e)}

    def _calculate_market_concentration(self, df: pd.DataFrame) -> str:
        """Calculate market concentration level"""
        if 'impression_share' not in df.columns:
            return 'unknown'

        # Calculate Herfindahl-Hirschman Index (HHI)
        shares = df['impression_share'].values * 100
        hhi = np.sum(shares ** 2)

        if hhi > 2500:
            return 'highly_concentrated'
        elif hhi > 1500:
            return 'moderately_concentrated'
        else:
            return 'competitive'

    def _calculate_competitive_intensity(self, df: pd.DataFrame) -> str:
        """Calculate competitive intensity level"""
        if len(df) < 2:
            return 'low'

        # Factors: number of competitors, overlap rates, position above rates
        num_competitors = len(df)
        avg_overlap = df['overlap_rate'].mean() if 'overlap_rate' in df.columns else 0
        avg_position_above = df['position_above_rate'].mean() if 'position_above_rate' in df.columns else 0

        intensity_score = (
            (num_competitors / 10) * 0.3 +
            avg_overlap * 0.4 +
            avg_position_above * 0.3
        )

        if intensity_score > 0.7:
            return 'very_high'
        elif intensity_score > 0.5:
            return 'high'
        elif intensity_score > 0.3:
            return 'moderate'
        else:
            return 'low'

    def _calculate_competitor_strength(self, metrics: Dict[str, Any]) -> int:
        """Calculate competitor strength score (0-100)"""
        score = 0

        # Impression share (0-30 points)
        score += min(metrics['impression_share'] * 0.3, 30)

        # Position above rate (0-25 points)
        score += min(metrics['position_above_rate'] * 0.25, 25)

        # Top of page rate (0-25 points)
        score += min(metrics['top_of_page_rate'] * 0.25, 25)

        # Overlap rate (0-20 points)
        score += min(metrics['overlap_rate'] * 0.2, 20)

        return int(min(score, 100))

    def _classify_competitor(self, metrics: Dict[str, Any]) -> str:
        """Classify competitor type"""
        strength = metrics['competitive_strength']
        overlap = metrics['overlap_rate']

        if strength > 70 and overlap > 60:
            return 'dominant_rival'
        elif strength > 50 and overlap > 40:
            return 'direct_competitor'
        elif strength < 30 and overlap > 30:
            return 'emerging_threat'
        elif overlap < 20:
            return 'peripheral_player'
        else:
            return 'moderate_competitor'

    def _determine_competitive_position(
        self,
        our_impression_share: float,
        competitor_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Determine our competitive position"""
        position = {
            'market_position': '',
            'rank': 0,
            'relative_strength': ''
        }

        # Determine rank
        competitors = sorted(
            competitor_metrics.values(),
            key=lambda x: x['impression_share'],
            reverse=True
        )

        our_rank = 1
        for comp in competitors:
            if comp['impression_share'] > our_impression_share:
                our_rank += 1

        position['rank'] = our_rank
        position['total_competitors'] = len(competitors) + 1

        # Determine position label
        if our_rank == 1:
            position['market_position'] = 'market_leader'
        elif our_rank <= 3:
            position['market_position'] = 'top_competitor'
        elif our_rank <= len(competitors) / 2:
            position['market_position'] = 'strong_competitor'
        else:
            position['market_position'] = 'challenger'

        # Relative strength
        if our_impression_share > 30:
            position['relative_strength'] = 'strong'
        elif our_impression_share > 15:
            position['relative_strength'] = 'moderate'
        else:
            position['relative_strength'] = 'developing'

        return position

    def _generate_competitive_recommendations(
        self,
        analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate competitive recommendations"""
        recommendations = []

        # Based on position
        position = analysis.get('competitive_position', {})
        if position.get('market_position') == 'challenger':
            recommendations.append("Focus on niche segments to build market share")
        elif position.get('market_position') == 'market_leader':
            recommendations.append("Defend position through innovation and quality")

        # Based on threats
        if analysis['threats']:
            high_threats = [t for t in analysis['threats'] if t.get('severity') == 'high']
            if high_threats:
                recommendations.append(f"Address {len(high_threats)} high-severity competitive threats")

        # Based on opportunities
        if analysis['opportunities']:
            recommendations.append(f"Exploit {len(analysis['opportunities'])} competitive opportunities identified")

        # Based on gaps
        if analysis.get('competitive_gaps'):
            recommendations.append("Close competitive gaps through targeted optimization")

        return recommendations[:5]

    def _identify_competitive_gaps(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify gaps in competitive coverage"""
        gaps = []

        if 'top_of_page_rate' in df.columns:
            our_top_rate = df[df.get('is_you', False)]['top_of_page_rate'].iloc[0] if any(df.get('is_you', False)) else 0
            competitor_avg = df[~df.get('is_you', False)]['top_of_page_rate'].mean()

            if competitor_avg > our_top_rate + 0.2:
                gaps.append({
                    'type': 'visibility_gap',
                    'metric': 'top_of_page_rate',
                    'our_value': round(our_top_rate * 100, 2),
                    'competitor_avg': round(competitor_avg * 100, 2),
                    'gap': round((competitor_avg - our_top_rate) * 100, 2)
                })

        return gaps

    def _calculate_keyword_competition_score(self, row: pd.Series) -> float:
        """Calculate competition score for a keyword"""
        score = 0

        # Competition level
        if row.get('competition') == 'HIGH':
            score += 0.7
        elif row.get('competition') == 'MEDIUM':
            score += 0.5
        else:
            score += 0.3

        # CPC relative to average
        if 'avg_cpc' in row and row['avg_cpc'] > 0:
            # Higher CPC indicates more competition
            cpc_factor = min(row['avg_cpc'] / 10, 1)  # Normalize to 0-1
            score = (score * 0.7) + (cpc_factor * 0.3)

        return round(score, 2)

    def _calculate_opportunity_score(self, row: pd.Series) -> float:
        """Calculate opportunity score for a keyword"""
        score = 0

        # High volume, low competition is ideal
        if row.get('search_volume', 0) > 5000:
            score += 0.4
        elif row.get('search_volume', 0) > 1000:
            score += 0.2

        if row.get('competition') == 'LOW':
            score += 0.3
        elif row.get('competition') == 'MEDIUM':
            score += 0.1

        # Low CPC is good
        if row.get('avg_cpc', 999) < 1:
            score += 0.3
        elif row.get('avg_cpc', 999) < 3:
            score += 0.2

        return round(score, 2)

    def _suggest_competition_strategy(self, row: pd.Series) -> str:
        """Suggest strategy for high competition keywords"""
        if row.get('avg_position', 999) > 3:
            return 'Increase bids to improve position'
        elif row.get('quality_score', 0) < 7:
            return 'Focus on quality score improvement'
        elif row.get('impression_share', 0) < 0.5:
            return 'Expand match types and increase budget'
        else:
            return 'Maintain current strategy, monitor competitors'

    def _identify_keyword_gaps(
        self,
        our_keywords: set,
        competitor_data: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """Identify keywords competitors use but we don't"""
        gaps = []

        for competitor, keywords in competitor_data.items():
            competitor_keywords = set(keywords)
            missing_keywords = competitor_keywords - our_keywords

            if missing_keywords:
                gaps.append({
                    'competitor': competitor,
                    'missing_keywords': list(missing_keywords)[:10],
                    'count': len(missing_keywords),
                    'priority': 'high' if len(missing_keywords) > 20 else 'medium'
                })

        return gaps

    def _calculate_lost_sov_impact(
        self,
        data: Dict[str, Any],
        loss_type: str
    ) -> str:
        """Calculate impact of lost share of voice"""
        if loss_type == 'budget':
            lost = data.get('search_lost_impression_share_budget', 0)
        else:
            lost = data.get('search_lost_impression_share_rank', 0)

        if lost > 0.3:
            return 'critical'
        elif lost > 0.15:
            return 'high'
        elif lost > 0.05:
            return 'moderate'
        else:
            return 'low'

    def _analyze_sov_trend(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze share of voice trend"""
        if 'search_impression_share' not in df.columns:
            return {}

        values = df['search_impression_share'].values
        dates = pd.to_datetime(df['date']) if 'date' in df.columns else pd.date_range(start='2024-01-01', periods=len(values))

        # Calculate trend
        x = np.arange(len(values))
        slope, intercept, r_value, p_value, std_err = np.polyfit(x, values, 1, full=True)[:5]

        return {
            'direction': 'increasing' if slope > 0 else 'decreasing',
            'change_rate': round(slope * 100, 3),
            'current': round(values[-1] * 100, 2),
            'previous': round(values[0] * 100, 2),
            'total_change': round((values[-1] - values[0]) * 100, 2)
        }

    def _benchmark_sov(self, current_sov: Dict[str, Any]) -> Dict[str, Any]:
        """Benchmark SOV against industry standards"""
        benchmarks = {
            'poor': {'min': 0, 'max': 10},
            'below_average': {'min': 10, 'max': 25},
            'average': {'min': 25, 'max': 50},
            'good': {'min': 50, 'max': 75},
            'excellent': {'min': 75, 'max': 100}
        }

        search_is = current_sov.get('search_impression_share', 0)

        for level, range_vals in benchmarks.items():
            if range_vals['min'] <= search_is < range_vals['max']:
                return {
                    'performance_level': level,
                    'percentile_estimate': self._estimate_percentile(search_is),
                    'improvement_potential': 100 - search_is
                }

        return {'performance_level': 'unknown'}

    def _estimate_percentile(self, impression_share: float) -> int:
        """Estimate percentile ranking based on impression share"""
        # Rough estimation based on typical distributions
        if impression_share < 10:
            return 20
        elif impression_share < 25:
            return 40
        elif impression_share < 50:
            return 60
        elif impression_share < 75:
            return 80
        else:
            return 95

    def _classify_performance(self, metric: str, ratio: float) -> str:
        """Classify performance relative to benchmark"""
        if ratio > 20:
            return 'excellent'
        elif ratio > 0:
            return 'above_average'
        elif ratio > -20:
            return 'below_average'
        else:
            return 'poor'

    def _calculate_positioning_score(self, comparisons: Dict[str, Any]) -> int:
        """Calculate overall positioning score"""
        score = 50  # Start at neutral

        for metric, data in comparisons.items():
            performance = data['performance']

            # Weight different metrics
            weight = 1.0
            if metric in ['avg_conversion_rate', 'avg_quality_score']:
                weight = 1.5
            elif metric in ['avg_ctr', 'avg_position']:
                weight = 1.2

            # Adjust score based on performance
            if performance > 0:
                score += min(performance * weight * 0.5, 25)
            else:
                score += max(performance * weight * 0.3, -25)

        return int(max(0, min(100, score)))

    def _generate_positioning_recommendations(
        self,
        analysis: Dict[str, Any],
        comparisons: Dict[str, Any]
    ) -> List[str]:
        """Generate strategic positioning recommendations"""
        recommendations = []

        score = analysis['positioning_score']

        if score < 40:
            recommendations.append("Urgent: Comprehensive optimization needed to remain competitive")
        elif score < 60:
            recommendations.append("Focus on improving weak areas to reach industry benchmarks")
        elif score < 80:
            recommendations.append("Build on strengths while addressing specific gaps")
        else:
            recommendations.append("Maintain leadership position through continuous innovation")

        # Specific recommendations based on weaknesses
        for weakness in analysis['weaknesses'][:2]:
            metric = weakness['metric']
            if metric == 'avg_ctr':
                recommendations.append("Improve ad relevance and test new formats to increase CTR")
            elif metric == 'avg_conversion_rate':
                recommendations.append("Optimize conversion funnel and landing pages")
            elif metric == 'avg_quality_score':
                recommendations.append("Focus on Quality Score factors: relevance, CTR, and landing pages")

        return recommendations[:5]

    def _determine_market_position(self, score: int) -> str:
        """Determine market position based on score"""
        if score >= 80:
            return 'market_leader'
        elif score >= 60:
            return 'strong_competitor'
        elif score >= 40:
            return 'average_performer'
        else:
            return 'needs_improvement'

    def get_tools(self) -> List[Tool]:
        """Get LangChain tools for competitor analysis"""
        return [
            Tool(
                name="analyze_auction_insights",
                func=self.analyze_auction_insights,
                description="Analyze Google Ads Auction Insights for competitive intelligence"
            ),
            Tool(
                name="analyze_competitive_keywords",
                func=self.analyze_competitive_keywords,
                description="Analyze competitive keyword landscape and opportunities"
            ),
            Tool(
                name="analyze_share_of_voice",
                func=self.analyze_share_of_voice,
                description="Analyze share of voice and market presence"
            ),
            Tool(
                name="analyze_competitive_positioning",
                func=self.analyze_competitive_positioning,
                description="Analyze competitive positioning and market standing"
            )
        ]