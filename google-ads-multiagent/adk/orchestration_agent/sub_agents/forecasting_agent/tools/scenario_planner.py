"""
Scenario planning tools for Forecasting Agent
"""
from typing import Dict, List, Any, Optional, Tuple
from langchain.tools import Tool
from loguru import logger
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats
import itertools


class ScenarioPlanner:
    """Plans and simulates various scenarios for Google Ads campaigns"""

    def __init__(self):
        logger.info("Scenario Planner initialized")

    def create_what_if_scenarios(
        self,
        baseline_data: Dict[str, Any],
        variables: List[Dict[str, Any]],
        constraints: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create what-if scenarios for different variables

        Args:
            baseline_data: Current/baseline performance data
            variables: Variables to modify in scenarios
            constraints: Constraints to apply

        Returns:
            Multiple scenarios with projected outcomes
        """
        try:
            scenarios = {
                'baseline': baseline_data,
                'scenarios': [],
                'comparison_matrix': {},
                'optimal_scenario': {},
                'risk_assessment': {},
                'recommendations': []
            }

            # Generate scenarios for each variable
            for variable in variables:
                var_scenarios = self._generate_variable_scenarios(
                    baseline_data,
                    variable,
                    constraints
                )
                scenarios['scenarios'].extend(var_scenarios)

            # Generate combination scenarios
            if len(variables) > 1:
                combo_scenarios = self._generate_combination_scenarios(
                    baseline_data,
                    variables,
                    constraints
                )
                scenarios['scenarios'].extend(combo_scenarios)

            # Create comparison matrix
            scenarios['comparison_matrix'] = self._create_comparison_matrix(
                scenarios['scenarios'],
                baseline_data
            )

            # Identify optimal scenario
            scenarios['optimal_scenario'] = self._identify_optimal_scenario(
                scenarios['scenarios'],
                constraints
            )

            # Assess risks
            scenarios['risk_assessment'] = self._assess_scenario_risks(
                scenarios['scenarios']
            )

            # Generate recommendations
            scenarios['recommendations'] = self._generate_scenario_recommendations(
                scenarios
            )

            return scenarios

        except Exception as e:
            logger.error(f"Error creating what-if scenarios: {e}")
            return {"error": str(e)}

    def simulate_strategy_changes(
        self,
        current_strategy: Dict[str, Any],
        new_strategies: List[Dict[str, Any]],
        simulation_period: int = 30
    ) -> Dict[str, Any]:
        """
        Simulate impact of strategy changes

        Args:
            current_strategy: Current strategy configuration
            new_strategies: New strategies to simulate
            simulation_period: Days to simulate

        Returns:
            Simulation results for each strategy
        """
        try:
            simulations = {
                'current_strategy': current_strategy,
                'simulation_period': simulation_period,
                'strategy_simulations': [],
                'performance_comparison': {},
                'transition_plan': {},
                'recommendations': []
            }

            # Simulate each new strategy
            for strategy in new_strategies:
                simulation = self._simulate_single_strategy(
                    current_strategy,
                    strategy,
                    simulation_period
                )
                simulations['strategy_simulations'].append(simulation)

            # Compare performance
            simulations['performance_comparison'] = self._compare_strategy_performance(
                simulations['strategy_simulations']
            )

            # Create transition plan for best strategy
            best_strategy = self._identify_best_strategy(
                simulations['strategy_simulations']
            )
            if best_strategy:
                simulations['transition_plan'] = self._create_transition_plan(
                    current_strategy,
                    best_strategy
                )

            # Generate recommendations
            simulations['recommendations'] = self._generate_strategy_recommendations(
                simulations
            )

            return simulations

        except Exception as e:
            logger.error(f"Error simulating strategy changes: {e}")
            return {"error": str(e)}

    def plan_budget_scenarios(
        self,
        current_budget: float,
        performance_data: List[Dict[str, Any]],
        budget_options: List[float] = None
    ) -> Dict[str, Any]:
        """
        Plan scenarios for different budget levels

        Args:
            current_budget: Current budget
            performance_data: Historical performance data
            budget_options: Budget levels to test

        Returns:
            Budget scenario analysis
        """
        try:
            if not budget_options:
                # Default budget scenarios
                budget_options = [
                    current_budget * 0.5,   # 50% reduction
                    current_budget * 0.75,  # 25% reduction
                    current_budget,         # Current
                    current_budget * 1.25,  # 25% increase
                    current_budget * 1.5,   # 50% increase
                    current_budget * 2.0    # Double
                ]

            df = pd.DataFrame(performance_data) if performance_data else pd.DataFrame()

            budget_scenarios = {
                'current_budget': current_budget,
                'scenarios': [],
                'efficiency_curve': {},
                'optimal_budget': {},
                'diminishing_returns': {},
                'recommendations': []
            }

            # Generate scenario for each budget level
            for budget in budget_options:
                scenario = self._simulate_budget_scenario(
                    budget,
                    df,
                    current_budget
                )
                budget_scenarios['scenarios'].append(scenario)

            # Calculate efficiency curve
            budget_scenarios['efficiency_curve'] = self._calculate_efficiency_curve(
                budget_scenarios['scenarios']
            )

            # Find optimal budget
            budget_scenarios['optimal_budget'] = self._find_optimal_budget(
                budget_scenarios['scenarios'],
                budget_scenarios['efficiency_curve']
            )

            # Identify diminishing returns point
            budget_scenarios['diminishing_returns'] = self._find_diminishing_returns_point(
                budget_scenarios['scenarios']
            )

            # Generate recommendations
            budget_scenarios['recommendations'] = self._generate_budget_scenario_recommendations(
                budget_scenarios
            )

            return budget_scenarios

        except Exception as e:
            logger.error(f"Error planning budget scenarios: {e}")
            return {"error": str(e)}

    def simulate_competitive_scenarios(
        self,
        market_data: Dict[str, Any],
        competitive_actions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Simulate competitive market scenarios

        Args:
            market_data: Current market data
            competitive_actions: Potential competitive actions

        Returns:
            Competitive scenario simulations
        """
        try:
            competitive_scenarios = {
                'current_market': market_data,
                'scenarios': [],
                'impact_analysis': {},
                'response_strategies': [],
                'recommendations': []
            }

            # Simulate each competitive action
            for action in competitive_actions:
                scenario = self._simulate_competitive_action(
                    market_data,
                    action
                )
                competitive_scenarios['scenarios'].append(scenario)

            # Analyze impact
            competitive_scenarios['impact_analysis'] = self._analyze_competitive_impact(
                competitive_scenarios['scenarios']
            )

            # Generate response strategies
            competitive_scenarios['response_strategies'] = self._generate_response_strategies(
                competitive_scenarios['scenarios']
            )

            # Generate recommendations
            competitive_scenarios['recommendations'] = self._generate_competitive_recommendations(
                competitive_scenarios
            )

            return competitive_scenarios

        except Exception as e:
            logger.error(f"Error simulating competitive scenarios: {e}")
            return {"error": str(e)}

    def _generate_variable_scenarios(
        self,
        baseline: Dict[str, Any],
        variable: Dict[str, Any],
        constraints: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate scenarios for a single variable"""
        scenarios = []

        var_name = variable.get('name', 'unknown')
        var_type = variable.get('type', 'continuous')
        current_value = baseline.get(var_name, 0)

        if var_type == 'continuous':
            # Generate range of values
            min_val = variable.get('min', current_value * 0.5)
            max_val = variable.get('max', current_value * 1.5)
            steps = variable.get('steps', 5)

            for value in np.linspace(min_val, max_val, steps):
                scenario = {
                    'name': f"{var_name}_{value:.2f}",
                    'variable': var_name,
                    'value': value,
                    'change_from_baseline': value - current_value,
                    'change_percent': ((value - current_value) / current_value * 100) if current_value > 0 else 0,
                    'projected_impact': self._project_variable_impact(
                        baseline,
                        var_name,
                        value
                    )
                }
                scenarios.append(scenario)

        elif var_type == 'categorical':
            # Generate scenarios for each category
            categories = variable.get('categories', [])
            for category in categories:
                scenario = {
                    'name': f"{var_name}_{category}",
                    'variable': var_name,
                    'value': category,
                    'change_from_baseline': f"from {baseline.get(var_name)} to {category}",
                    'projected_impact': self._project_categorical_impact(
                        baseline,
                        var_name,
                        category
                    )
                }
                scenarios.append(scenario)

        return scenarios

    def _generate_combination_scenarios(
        self,
        baseline: Dict[str, Any],
        variables: List[Dict[str, Any]],
        constraints: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate combination scenarios for multiple variables"""
        scenarios = []

        # Limit combinations to avoid explosion
        max_combinations = 10

        # Create representative combinations
        combinations = [
            {'name': 'Conservative', 'multipliers': [0.8, 0.8]},
            {'name': 'Moderate', 'multipliers': [1.1, 1.1]},
            {'name': 'Aggressive', 'multipliers': [1.3, 1.3]},
            {'name': 'Mixed_High_Budget', 'multipliers': [1.5, 0.9]},
            {'name': 'Mixed_High_Efficiency', 'multipliers': [0.9, 1.5]}
        ]

        for combo in combinations[:max_combinations]:
            scenario = {
                'name': f"Combo_{combo['name']}",
                'variables': {},
                'projected_impact': {}
            }

            # Apply multipliers to each variable
            for i, variable in enumerate(variables[:2]):  # Limit to 2 variables
                var_name = variable.get('name', f'var_{i}')
                current_value = baseline.get(var_name, 0)

                if i < len(combo['multipliers']):
                    new_value = current_value * combo['multipliers'][i]
                    scenario['variables'][var_name] = new_value

            # Project combined impact
            scenario['projected_impact'] = self._project_combined_impact(
                baseline,
                scenario['variables']
            )

            scenarios.append(scenario)

        return scenarios

    def _project_variable_impact(
        self,
        baseline: Dict[str, Any],
        variable: str,
        value: float
    ) -> Dict[str, Any]:
        """Project impact of variable change"""
        impact = {}

        current_value = baseline.get(variable, 0)
        if current_value == 0:
            return impact

        change_ratio = value / current_value

        # Project based on variable type
        if variable == 'budget':
            # Budget changes affect volume with diminishing returns
            impact['impressions'] = baseline.get('impressions', 0) * (change_ratio ** 0.8)
            impact['clicks'] = baseline.get('clicks', 0) * (change_ratio ** 0.85)
            impact['conversions'] = baseline.get('conversions', 0) * (change_ratio ** 0.7)
            impact['cost'] = value

        elif variable == 'bid':
            # Bid changes affect position and costs
            impact['avg_position'] = max(1, baseline.get('avg_position', 3) / (change_ratio ** 0.5))
            impact['cpc'] = baseline.get('cpc', 0) * change_ratio
            impact['clicks'] = baseline.get('clicks', 0) * (change_ratio ** 0.6)
            impact['conversions'] = baseline.get('conversions', 0) * (change_ratio ** 0.5)

        elif variable == 'target_cpa':
            # Target CPA affects volume and efficiency
            impact['conversions'] = baseline.get('conversions', 0) * (1 / change_ratio ** 0.5)
            impact['cost'] = value * impact['conversions']
            impact['cpa'] = value

        return impact

    def _project_categorical_impact(
        self,
        baseline: Dict[str, Any],
        variable: str,
        category: str
    ) -> Dict[str, Any]:
        """Project impact of categorical variable change"""
        impact = {}

        # Simplified projections based on category
        if variable == 'bidding_strategy':
            if category == 'maximize_conversions':
                impact['conversions'] = baseline.get('conversions', 0) * 1.15
                impact['cost'] = baseline.get('cost', 0) * 1.1
            elif category == 'target_roas':
                impact['conversion_value'] = baseline.get('conversion_value', 0) * 1.1
                impact['cost'] = baseline.get('cost', 0) * 0.95
            elif category == 'manual_cpc':
                impact = baseline.copy()  # No change expected

        elif variable == 'network':
            if category == 'search_only':
                impact['quality_score'] = baseline.get('quality_score', 5) + 1
                impact['ctr'] = baseline.get('ctr', 0) * 1.2
            elif category == 'search_and_display':
                impact['impressions'] = baseline.get('impressions', 0) * 2
                impact['ctr'] = baseline.get('ctr', 0) * 0.6

        return impact

    def _project_combined_impact(
        self,
        baseline: Dict[str, Any],
        variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Project combined impact of multiple variable changes"""
        impact = baseline.copy()

        # Apply each variable change
        for var_name, var_value in variables.items():
            single_impact = self._project_variable_impact(baseline, var_name, var_value)

            # Combine impacts (simplified approach)
            for metric, value in single_impact.items():
                if metric in impact:
                    # Average the impacts
                    impact[metric] = (impact[metric] + value) / 2
                else:
                    impact[metric] = value

        return impact

    def _create_comparison_matrix(
        self,
        scenarios: List[Dict[str, Any]],
        baseline: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create comparison matrix for scenarios"""
        matrix = {
            'scenarios': [],
            'metrics': ['cost', 'conversions', 'revenue', 'roi', 'cpa']
        }

        for scenario in scenarios:
            comparison = {
                'name': scenario['name'],
                'metrics': {}
            }

            projected = scenario.get('projected_impact', {})

            # Calculate key metrics
            comparison['metrics']['cost'] = projected.get('cost', baseline.get('cost', 0))
            comparison['metrics']['conversions'] = projected.get('conversions', baseline.get('conversions', 0))
            comparison['metrics']['revenue'] = projected.get('conversion_value', baseline.get('conversion_value', 0))

            # Calculate derived metrics
            cost = comparison['metrics']['cost']
            conversions = comparison['metrics']['conversions']
            revenue = comparison['metrics']['revenue']

            comparison['metrics']['roi'] = ((revenue - cost) / cost * 100) if cost > 0 else 0
            comparison['metrics']['cpa'] = (cost / conversions) if conversions > 0 else 0

            matrix['scenarios'].append(comparison)

        return matrix

    def _identify_optimal_scenario(
        self,
        scenarios: List[Dict[str, Any]],
        constraints: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Identify optimal scenario based on constraints"""
        if not scenarios:
            return {}

        # Score each scenario
        scored_scenarios = []

        for scenario in scenarios:
            score = 0
            projected = scenario.get('projected_impact', {})

            # Score based on key metrics
            conversions = projected.get('conversions', 0)
            cost = projected.get('cost', 0)
            revenue = projected.get('conversion_value', 0)

            # ROI component
            if cost > 0:
                roi = (revenue - cost) / cost
                score += roi * 40  # 40% weight

            # Volume component
            score += (conversions / 100) * 30  # 30% weight

            # Efficiency component
            if conversions > 0:
                cpa = cost / conversions
                efficiency_score = 100 / (1 + cpa)  # Lower CPA = higher score
                score += efficiency_score * 30  # 30% weight

            # Apply constraints
            if constraints:
                if 'max_budget' in constraints and cost > constraints['max_budget']:
                    score *= 0.5  # Penalize over-budget scenarios

                if 'min_conversions' in constraints and conversions < constraints['min_conversions']:
                    score *= 0.5  # Penalize under-performing scenarios

            scored_scenarios.append({
                'scenario': scenario,
                'score': score
            })

        # Find optimal
        optimal = max(scored_scenarios, key=lambda x: x['score'])

        return {
            'scenario': optimal['scenario'],
            'score': optimal['score'],
            'reason': 'Highest combined score for ROI, volume, and efficiency'
        }

    def _assess_scenario_risks(
        self,
        scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess risks for each scenario"""
        risk_assessment = {
            'scenario_risks': [],
            'high_risk_scenarios': [],
            'low_risk_scenarios': []
        }

        for scenario in scenarios:
            risks = []
            risk_score = 0

            # Check for extreme changes
            if 'change_percent' in scenario:
                if abs(scenario['change_percent']) > 50:
                    risks.append('Extreme change from baseline')
                    risk_score += 3

            # Check projected metrics
            projected = scenario.get('projected_impact', {})

            # High cost risk
            if projected.get('cost', 0) > scenario.get('baseline_cost', 0) * 2:
                risks.append('Significant cost increase')
                risk_score += 2

            # Low conversion risk
            if projected.get('conversions', 0) < scenario.get('baseline_conversions', 0) * 0.5:
                risks.append('Significant conversion decrease')
                risk_score += 3

            scenario_risk = {
                'scenario': scenario['name'],
                'risks': risks,
                'risk_score': risk_score,
                'risk_level': 'high' if risk_score >= 4 else 'medium' if risk_score >= 2 else 'low'
            }

            risk_assessment['scenario_risks'].append(scenario_risk)

            if scenario_risk['risk_level'] == 'high':
                risk_assessment['high_risk_scenarios'].append(scenario['name'])
            elif scenario_risk['risk_level'] == 'low':
                risk_assessment['low_risk_scenarios'].append(scenario['name'])

        return risk_assessment

    def _generate_scenario_recommendations(
        self,
        scenarios: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations from scenario analysis"""
        recommendations = []

        # Optimal scenario recommendation
        optimal = scenarios.get('optimal_scenario', {})
        if optimal:
            scenario_name = optimal.get('scenario', {}).get('name', 'Unknown')
            recommendations.append(f"Optimal scenario: {scenario_name}")

        # Risk-based recommendations
        risks = scenarios.get('risk_assessment', {})
        high_risk = risks.get('high_risk_scenarios', [])
        if high_risk:
            recommendations.append(f"Avoid high-risk scenarios: {', '.join(high_risk[:3])}")

        # Look for quick wins
        for scenario in scenarios.get('scenarios', []):
            if scenario.get('change_percent', 0) < 20:  # Small change
                impact = scenario.get('projected_impact', {})
                if impact.get('conversions', 0) > scenarios['baseline'].get('conversions', 0) * 1.1:
                    recommendations.append(f"Quick win: {scenario['name']} - small change, good impact")
                    break

        return recommendations[:5]

    def _simulate_single_strategy(
        self,
        current: Dict[str, Any],
        new_strategy: Dict[str, Any],
        period: int
    ) -> Dict[str, Any]:
        """Simulate a single strategy change"""
        simulation = {
            'strategy_name': new_strategy.get('name', 'Unknown'),
            'strategy_type': new_strategy.get('type', 'Unknown'),
            'simulation_period': period,
            'projected_performance': {},
            'transition_impact': {},
            'learning_period': {}
        }

        # Project performance after learning period
        if new_strategy['type'] == 'bidding_strategy':
            learning_days = 14  # Google Ads learning period

            # During learning period
            simulation['learning_period'] = {
                'duration': learning_days,
                'expected_volatility': 'high',
                'performance': 'below_average'
            }

            # After learning period
            if new_strategy['name'] == 'target_cpa':
                simulation['projected_performance'] = {
                    'conversions': current.get('conversions', 0) * 1.1,
                    'cost': current.get('cost', 0) * 0.95,
                    'cpa': new_strategy.get('target_cpa', current.get('cpa', 0))
                }
            elif new_strategy['name'] == 'target_roas':
                simulation['projected_performance'] = {
                    'conversion_value': current.get('conversion_value', 0) * 1.15,
                    'cost': current.get('cost', 0),
                    'roas': new_strategy.get('target_roas', 3.0)
                }

        # Calculate transition impact
        simulation['transition_impact'] = {
            'estimated_loss_during_learning': current.get('conversions', 0) * 0.1 * (learning_days / 30),
            'time_to_stability': f"{learning_days} days",
            'confidence': 'medium'
        }

        return simulation

    def _compare_strategy_performance(
        self,
        simulations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compare performance across strategies"""
        comparison = {
            'best_for_conversions': None,
            'best_for_efficiency': None,
            'best_for_revenue': None,
            'ranking': []
        }

        # Find best for each metric
        max_conversions = 0
        max_revenue = 0
        min_cpa = float('inf')

        for sim in simulations:
            perf = sim.get('projected_performance', {})

            conversions = perf.get('conversions', 0)
            if conversions > max_conversions:
                max_conversions = conversions
                comparison['best_for_conversions'] = sim['strategy_name']

            revenue = perf.get('conversion_value', 0)
            if revenue > max_revenue:
                max_revenue = revenue
                comparison['best_for_revenue'] = sim['strategy_name']

            cpa = perf.get('cpa', float('inf'))
            if cpa < min_cpa and cpa > 0:
                min_cpa = cpa
                comparison['best_for_efficiency'] = sim['strategy_name']

        # Create ranking
        for sim in simulations:
            perf = sim.get('projected_performance', {})

            # Calculate composite score
            score = 0
            score += (perf.get('conversions', 0) / max_conversions * 30) if max_conversions > 0 else 0
            score += (perf.get('conversion_value', 0) / max_revenue * 40) if max_revenue > 0 else 0
            score += ((min_cpa / perf.get('cpa', 1)) * 30) if perf.get('cpa', 0) > 0 else 0

            comparison['ranking'].append({
                'strategy': sim['strategy_name'],
                'score': round(score, 2)
            })

        comparison['ranking'].sort(key=lambda x: x['score'], reverse=True)

        return comparison

    def _identify_best_strategy(
        self,
        simulations: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Identify best strategy from simulations"""
        if not simulations:
            return None

        best_score = -1
        best_strategy = None

        for sim in simulations:
            score = 0
            perf = sim.get('projected_performance', {})

            # Score based on improvement over current
            if perf:
                score += perf.get('conversions', 0) * 0.3
                score += perf.get('conversion_value', 0) * 0.4
                score -= perf.get('cpa', 100) * 0.3

            if score > best_score:
                best_score = score
                best_strategy = sim

        return best_strategy

    def _create_transition_plan(
        self,
        current: Dict[str, Any],
        target_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create transition plan from current to target strategy"""
        plan = {
            'phases': [],
            'timeline': {},
            'risk_mitigation': [],
            'success_metrics': []
        }

        # Phase 1: Preparation
        plan['phases'].append({
            'phase': 1,
            'name': 'Preparation',
            'duration': '3-5 days',
            'actions': [
                'Audit current performance',
                'Set up tracking',
                'Document baseline metrics'
            ]
        })

        # Phase 2: Gradual transition
        plan['phases'].append({
            'phase': 2,
            'name': 'Gradual Transition',
            'duration': '7-14 days',
            'actions': [
                'Start with 20% of campaigns',
                'Monitor performance daily',
                'Adjust targets based on early results'
            ]
        })

        # Phase 3: Full implementation
        plan['phases'].append({
            'phase': 3,
            'name': 'Full Implementation',
            'duration': '14-21 days',
            'actions': [
                'Roll out to all campaigns',
                'Fine-tune settings',
                'Optimize based on learning'
            ]
        })

        # Timeline
        plan['timeline'] = {
            'total_duration': '30-45 days',
            'learning_period': '14 days',
            'optimization_period': '30 days'
        }

        # Risk mitigation
        plan['risk_mitigation'] = [
            'Keep 10% of budget in manual control',
            'Set conservative initial targets',
            'Daily monitoring during transition',
            'Prepare rollback plan'
        ]

        # Success metrics
        plan['success_metrics'] = [
            'CPA within 10% of target',
            'Conversion volume maintained or increased',
            'ROAS meets or exceeds baseline'
        ]

        return plan

    def _generate_strategy_recommendations(
        self,
        simulations: Dict[str, Any]
    ) -> List[str]:
        """Generate strategy recommendations"""
        recommendations = []

        # Best strategy recommendation
        comparison = simulations.get('performance_comparison', {})
        if comparison.get('ranking'):
            best = comparison['ranking'][0]['strategy']
            recommendations.append(f"Recommended strategy: {best}")

        # Transition plan recommendation
        if simulations.get('transition_plan'):
            timeline = simulations['transition_plan'].get('timeline', {})
            duration = timeline.get('total_duration', 'Unknown')
            recommendations.append(f"Allow {duration} for complete transition")

        # Risk recommendations
        for sim in simulations.get('strategy_simulations', []):
            if sim.get('learning_period', {}).get('expected_volatility') == 'high':
                recommendations.append("Expect performance volatility during learning period")
                break

        return recommendations[:5]

    def _simulate_budget_scenario(
        self,
        budget: float,
        historical_df: pd.DataFrame,
        current_budget: float
    ) -> Dict[str, Any]:
        """Simulate scenario for a specific budget"""
        scenario = {
            'budget': budget,
            'change_from_current': budget - current_budget,
            'change_percent': ((budget - current_budget) / current_budget * 100) if current_budget > 0 else 0,
            'projected_metrics': {},
            'efficiency_metrics': {}
        }

        if not historical_df.empty:
            # Calculate historical efficiency
            historical_cost = historical_df['cost'].sum() if 'cost' in historical_df else 1
            historical_conversions = historical_df['conversions'].sum() if 'conversions' in historical_df else 0
            historical_revenue = historical_df['conversion_value'].sum() if 'conversion_value' in historical_df else 0

            # Project metrics with diminishing returns
            budget_ratio = budget / historical_cost if historical_cost > 0 else 1

            # Apply diminishing returns formula
            efficiency_factor = 1 / (1 + 0.1 * max(0, budget_ratio - 1))  # Decreases as budget increases

            scenario['projected_metrics'] = {
                'impressions': historical_df['impressions'].sum() * (budget_ratio ** 0.9) if 'impressions' in historical_df else 0,
                'clicks': historical_df['clicks'].sum() * (budget_ratio ** 0.85) if 'clicks' in historical_df else 0,
                'conversions': historical_conversions * (budget_ratio ** 0.7) * efficiency_factor,
                'revenue': historical_revenue * (budget_ratio ** 0.75) * efficiency_factor
            }

            # Calculate efficiency metrics
            projected_conversions = scenario['projected_metrics']['conversions']
            projected_revenue = scenario['projected_metrics']['revenue']

            scenario['efficiency_metrics'] = {
                'cpa': (budget / projected_conversions) if projected_conversions > 0 else 0,
                'roas': (projected_revenue / budget) if budget > 0 else 0,
                'conversion_rate': (projected_conversions / scenario['projected_metrics']['clicks'] * 100)
                                  if scenario['projected_metrics']['clicks'] > 0 else 0
            }

        return scenario

    def _calculate_efficiency_curve(
        self,
        scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate efficiency curve across budget levels"""
        curve = {
            'budgets': [],
            'cpa_curve': [],
            'roas_curve': [],
            'marginal_cpa': [],
            'marginal_roas': []
        }

        sorted_scenarios = sorted(scenarios, key=lambda x: x['budget'])

        for i, scenario in enumerate(sorted_scenarios):
            budget = scenario['budget']
            curve['budgets'].append(budget)

            # CPA and ROAS curves
            cpa = scenario['efficiency_metrics'].get('cpa', 0)
            roas = scenario['efficiency_metrics'].get('roas', 0)

            curve['cpa_curve'].append(cpa)
            curve['roas_curve'].append(roas)

            # Calculate marginal metrics
            if i > 0:
                prev_scenario = sorted_scenarios[i-1]

                budget_increase = budget - prev_scenario['budget']
                conversions_increase = (scenario['projected_metrics']['conversions'] -
                                       prev_scenario['projected_metrics']['conversions'])
                revenue_increase = (scenario['projected_metrics']['revenue'] -
                                   prev_scenario['projected_metrics']['revenue'])

                marginal_cpa = (budget_increase / conversions_increase) if conversions_increase > 0 else float('inf')
                marginal_roas = (revenue_increase / budget_increase) if budget_increase > 0 else 0

                curve['marginal_cpa'].append(marginal_cpa)
                curve['marginal_roas'].append(marginal_roas)
            else:
                curve['marginal_cpa'].append(cpa)
                curve['marginal_roas'].append(roas)

        return curve

    def _find_optimal_budget(
        self,
        scenarios: List[Dict[str, Any]],
        efficiency_curve: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Find optimal budget based on efficiency"""
        optimal = {
            'budget': 0,
            'reason': '',
            'expected_performance': {}
        }

        # Find budget with best ROAS above minimum threshold
        min_roas_threshold = 2.0
        best_score = -1
        best_scenario = None

        for i, scenario in enumerate(scenarios):
            roas = scenario['efficiency_metrics'].get('roas', 0)
            conversions = scenario['projected_metrics'].get('conversions', 0)

            if roas >= min_roas_threshold:
                # Score based on efficiency and volume
                score = roas * 0.5 + (conversions / 100) * 0.5

                if score > best_score:
                    best_score = score
                    best_scenario = scenario

        if best_scenario:
            optimal['budget'] = best_scenario['budget']
            optimal['reason'] = 'Best balance of efficiency and volume'
            optimal['expected_performance'] = best_scenario['projected_metrics']
        else:
            # Fallback to scenario with best ROAS
            best_roas_scenario = max(scenarios, key=lambda x: x['efficiency_metrics'].get('roas', 0))
            optimal['budget'] = best_roas_scenario['budget']
            optimal['reason'] = 'Highest ROAS achieved'
            optimal['expected_performance'] = best_roas_scenario['projected_metrics']

        return optimal

    def _find_diminishing_returns_point(
        self,
        scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Find point of diminishing returns"""
        diminishing_point = {
            'budget': 0,
            'identified': False,
            'marginal_efficiency': {}
        }

        sorted_scenarios = sorted(scenarios, key=lambda x: x['budget'])

        for i in range(1, len(sorted_scenarios)):
            current = sorted_scenarios[i]
            previous = sorted_scenarios[i-1]

            # Calculate marginal ROAS
            budget_increase = current['budget'] - previous['budget']
            revenue_increase = (current['projected_metrics']['revenue'] -
                              previous['projected_metrics']['revenue'])

            if budget_increase > 0:
                marginal_roas = revenue_increase / budget_increase

                # Check if marginal ROAS falls below 1 (break-even)
                if marginal_roas < 1 and not diminishing_point['identified']:
                    diminishing_point['budget'] = current['budget']
                    diminishing_point['identified'] = True
                    diminishing_point['marginal_efficiency'] = {
                        'marginal_roas': marginal_roas,
                        'description': 'Additional spend generates less than $1 in revenue'
                    }
                    break

        if not diminishing_point['identified']:
            # Diminishing returns not reached in tested range
            diminishing_point['budget'] = sorted_scenarios[-1]['budget']
            diminishing_point['description'] = 'Diminishing returns not reached in tested range'

        return diminishing_point

    def _generate_budget_scenario_recommendations(
        self,
        budget_scenarios: Dict[str, Any]
    ) -> List[str]:
        """Generate budget scenario recommendations"""
        recommendations = []

        # Optimal budget recommendation
        optimal = budget_scenarios.get('optimal_budget', {})
        if optimal:
            recommendations.append(f"Optimal budget: ${optimal['budget']:.2f} - {optimal['reason']}")

        # Diminishing returns warning
        diminishing = budget_scenarios.get('diminishing_returns', {})
        if diminishing.get('identified'):
            recommendations.append(f"Diminishing returns begin at ${diminishing['budget']:.2f}")

        # Efficiency recommendations
        current_budget = budget_scenarios.get('current_budget', 0)
        for scenario in budget_scenarios.get('scenarios', []):
            if scenario['budget'] == current_budget:
                current_roas = scenario['efficiency_metrics'].get('roas', 0)
                if current_roas < 2:
                    recommendations.append("Current budget showing low ROAS - consider optimization before scaling")
                elif current_roas > 4:
                    recommendations.append("Current budget showing high ROAS - opportunity to scale")
                break

        return recommendations[:5]

    def _simulate_competitive_action(
        self,
        market_data: Dict[str, Any],
        action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulate a competitive action in the market"""
        scenario = {
            'action': action.get('type', 'unknown'),
            'competitor': action.get('competitor', 'unknown'),
            'magnitude': action.get('magnitude', 'medium'),
            'impact_on_market': {},
            'impact_on_us': {}
        }

        # Simulate based on action type
        if action['type'] == 'budget_increase':
            # Competitor increases budget
            increase_factor = {'low': 1.2, 'medium': 1.5, 'high': 2.0}.get(action['magnitude'], 1.3)

            scenario['impact_on_market'] = {
                'avg_cpc': market_data.get('avg_cpc', 2) * (1 + (increase_factor - 1) * 0.3),  # CPCs increase
                'impression_share_available': market_data.get('impression_share', 100) * 0.9  # Less share available
            }

            scenario['impact_on_us'] = {
                'impression_share': market_data.get('our_impression_share', 20) * 0.85,  # We lose share
                'cpc_increase': (increase_factor - 1) * 20,  # Our CPCs increase
                'position_change': -0.5  # Position worsens
            }

        elif action['type'] == 'new_entrant':
            # New competitor enters market
            scenario['impact_on_market'] = {
                'competition_level': 'increased',
                'avg_cpc': market_data.get('avg_cpc', 2) * 1.15,
                'total_competitors': market_data.get('competitors', 5) + 1
            }

            scenario['impact_on_us'] = {
                'impression_share': market_data.get('our_impression_share', 20) * 0.9,
                'cpc_increase': 10,
                'required_budget_increase': 15  # To maintain position
            }

        elif action['type'] == 'aggressive_bidding':
            # Competitor bids aggressively
            scenario['impact_on_market'] = {
                'avg_cpc': market_data.get('avg_cpc', 2) * 1.4,
                'auction_pressure': 'high'
            }

            scenario['impact_on_us'] = {
                'cpc_increase': 30,
                'quality_score_importance': 'critical',
                'recommended_response': 'Focus on quality score improvement'
            }

        return scenario

    def _analyze_competitive_impact(
        self,
        scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze impact of competitive scenarios"""
        analysis = {
            'most_threatening': None,
            'total_impact': {},
            'vulnerability_assessment': {}
        }

        max_threat_score = 0
        most_threatening = None

        for scenario in scenarios:
            impact = scenario.get('impact_on_us', {})

            # Calculate threat score
            threat_score = 0

            if impact.get('impression_share', 100) < 15:
                threat_score += 3

            if impact.get('cpc_increase', 0) > 25:
                threat_score += 2

            if impact.get('required_budget_increase', 0) > 20:
                threat_score += 2

            if threat_score > max_threat_score:
                max_threat_score = threat_score
                most_threatening = scenario

        analysis['most_threatening'] = most_threatening

        # Aggregate total impact
        total_cpc_increase = sum(s.get('impact_on_us', {}).get('cpc_increase', 0) for s in scenarios) / len(scenarios) if scenarios else 0
        total_share_loss = sum(s.get('impact_on_us', {}).get('impression_share', 100) for s in scenarios) / len(scenarios) if scenarios else 0

        analysis['total_impact'] = {
            'avg_cpc_increase': round(total_cpc_increase, 2),
            'avg_impression_share': round(total_share_loss, 2)
        }

        # Vulnerability assessment
        analysis['vulnerability_assessment'] = {
            'budget_flexibility': 'low' if total_cpc_increase > 20 else 'medium' if total_cpc_increase > 10 else 'high',
            'position_strength': 'weak' if total_share_loss < 15 else 'moderate' if total_share_loss < 25 else 'strong'
        }

        return analysis

    def _generate_response_strategies(
        self,
        scenarios: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate response strategies for competitive scenarios"""
        strategies = []

        for scenario in scenarios:
            action_type = scenario.get('action')

            if action_type == 'budget_increase':
                strategies.append({
                    'scenario': action_type,
                    'response': 'Quality Score Focus',
                    'tactics': [
                        'Improve ad relevance',
                        'Optimize landing pages',
                        'Refine keyword match types'
                    ],
                    'expected_outcome': 'Maintain position with lower CPC increase'
                })

            elif action_type == 'new_entrant':
                strategies.append({
                    'scenario': action_type,
                    'response': 'Defend Core Keywords',
                    'tactics': [
                        'Increase bids on brand terms',
                        'Strengthen remarketing',
                        'Launch competitive campaigns'
                    ],
                    'expected_outcome': 'Protect market share'
                })

            elif action_type == 'aggressive_bidding':
                strategies.append({
                    'scenario': action_type,
                    'response': 'Efficiency Optimization',
                    'tactics': [
                        'Focus on long-tail keywords',
                        'Implement day-parting',
                        'Use audience targeting'
                    ],
                    'expected_outcome': 'Maintain profitability'
                })

        return strategies

    def _generate_competitive_recommendations(
        self,
        competitive_scenarios: Dict[str, Any]
    ) -> List[str]:
        """Generate competitive scenario recommendations"""
        recommendations = []

        # Most threatening scenario
        most_threatening = competitive_scenarios.get('impact_analysis', {}).get('most_threatening')
        if most_threatening:
            action = most_threatening.get('action', 'unknown')
            recommendations.append(f"Prepare for {action} - highest threat level")

        # Vulnerability recommendations
        vulnerability = competitive_scenarios.get('impact_analysis', {}).get('vulnerability_assessment', {})
        if vulnerability.get('budget_flexibility') == 'low':
            recommendations.append("Limited budget flexibility - focus on efficiency improvements")

        if vulnerability.get('position_strength') == 'weak':
            recommendations.append("Weak market position - invest in differentiation")

        # Response strategy recommendations
        response_strategies = competitive_scenarios.get('response_strategies', [])
        if response_strategies:
            primary_response = response_strategies[0]
            recommendations.append(f"Primary response: {primary_response['response']}")

        return recommendations[:5]

    def get_tools(self) -> List[Tool]:
        """Get LangChain tools for scenario planning"""
        return [
            Tool(
                name="create_what_if_scenarios",
                func=self.create_what_if_scenarios,
                description="Create what-if scenarios for different variables"
            ),
            Tool(
                name="simulate_strategy_changes",
                func=self.simulate_strategy_changes,
                description="Simulate impact of strategy changes"
            ),
            Tool(
                name="plan_budget_scenarios",
                func=self.plan_budget_scenarios,
                description="Plan scenarios for different budget levels"
            ),
            Tool(
                name="simulate_competitive_scenarios",
                func=self.simulate_competitive_scenarios,
                description="Simulate competitive market scenarios"
            )
        ]