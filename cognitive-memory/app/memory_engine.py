"""
Intelligence Memory Engine - Pattern Recognition and Prediction
Core cognitive processing with continuous learning capabilities
"""

import hashlib
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from database import db


class IntelligenceEngine:
    """
    Hyper-intelligent response system with pattern recognition
    Gets smarter with every interaction through persistent memory
    """

    def __init__(self):
        self.context_window: List[Dict] = []
        self.max_context_size = 50
        self.learning_rate = 0.1

    async def initialize(self):
        """Initialize database connection and load existing patterns"""
        await db.init_pool()
        print("✓ Intelligence Engine initialized")

    async def shutdown(self):
        """Graceful shutdown"""
        await db.close_pool()
        print("✓ Intelligence Engine shutdown")

    # ========================================================================
    # CORE PROCESSING PIPELINE
    # ========================================================================

    async def process_input(
        self,
        input_data: Dict[str, Any],
        predict_future: bool = True,
        cascade_depth: int = 5
    ) -> Dict[str, Any]:
        """
        Main processing pipeline:
        1. Store interaction (triggers intelligence accumulation)
        2. Find relevant patterns
        3. Check optimization cache
        4. Predict cascade effects
        5. Generate optimized response
        6. Learn from interaction
        """

        # Add to context window
        self._add_to_context(input_data)

        # 1. Store the interaction (automatically accumulates intelligence)
        memory_record = await db.store_interaction(
            interaction=input_data,
            future_implications=input_data.get('expected_outcomes', []),
            causality_chain=input_data.get('related_decisions', [])
        )

        # 2. Find relevant patterns from past interactions
        patterns = await db.find_patterns(
            context={'input': input_data.get('context', '')},
            similarity_threshold=0.6
        )

        # 3. Check if we have a cached optimal solution
        cached_solution = await db.get_cached_solution(
            problem_signature={'context': input_data.get('context', '')}
        )

        # 4. Predict future cascade effects if requested
        cascades = []
        if predict_future and input_data.get('decision'):
            cascades = await db.predict_cascade_effects(
                decision=input_data['decision'],
                depth=cascade_depth
            )

        # 5. Generate intelligent response
        response = await self._generate_response(
            input_data=input_data,
            patterns=patterns,
            cached_solution=cached_solution,
            cascades=cascades,
            intelligence_delta=memory_record['intelligence_delta']
        )

        # 6. Learn from this interaction
        await self._learn_from_interaction(input_data, response)

        return response

    # ========================================================================
    # RESPONSE GENERATION
    # ========================================================================

    async def _generate_response(
        self,
        input_data: Dict[str, Any],
        patterns: List[Dict],
        cached_solution: Optional[Dict],
        cascades: List[Dict],
        intelligence_delta: float
    ) -> Dict[str, Any]:
        """
        Generate hyper-intelligent response using all available data
        Format: SOLUTION → FUTURE STATE → RISK MATRIX → BETTER PATH
        """

        # Direct solution (use cached if available, otherwise compute)
        direct_solution = self._compute_optimal_solution(
            input_data,
            patterns,
            cached_solution
        )

        # Future implications analysis
        future_analysis = self._analyze_future_state(cascades, patterns)

        # Risk assessment
        risk_matrix = self._assess_risks(cascades, patterns)

        # Optimization suggestions
        optimizations = self._generate_optimizations(patterns, direct_solution)

        # Pattern insights
        pattern_insights = self._extract_pattern_insights(patterns)

        return {
            'direct_solution': direct_solution,
            'future_implications': future_analysis,
            'risk_matrix': risk_matrix,
            'optimization_path': optimizations,
            'pattern_insights': pattern_insights,
            'intelligence_metrics': {
                'delta': round(intelligence_delta, 3),
                'patterns_matched': len(patterns),
                'cache_hit': cached_solution is not None,
                'prediction_depth': len(cascades),
                'timestamp': datetime.utcnow().isoformat()
            },
            'brutal_honesty': self._generate_honest_assessment(
                input_data,
                direct_solution,
                patterns
            )
        }

    def _compute_optimal_solution(
        self,
        input_data: Dict[str, Any],
        patterns: List[Dict],
        cached_solution: Optional[Dict]
    ) -> Dict[str, Any]:
        """Compute optimal solution using learned patterns"""

        if cached_solution:
            return {
                'approach': 'cached_optimal',
                'solution': cached_solution['optimal_solution'],
                'performance': cached_solution.get('performance_metrics', {}),
                'source': 'optimization_cache',
                'confidence': 0.95
            }

        # Apply best matching pattern
        if patterns and patterns[0]['prediction_accuracy'] > 0.7:
            best_pattern = patterns[0]
            return {
                'approach': 'pattern_based',
                'solution': best_pattern.get('learned_optimization', 'Apply proven pattern'),
                'pattern_type': best_pattern['pattern_type'],
                'confidence': best_pattern['prediction_accuracy'],
                'source': 'learned_patterns'
            }

        # Fallback: analyze input and provide baseline solution
        return {
            'approach': 'analytical',
            'solution': self._analyze_and_solve(input_data),
            'confidence': 0.6,
            'source': 'direct_analysis',
            'note': 'No cached solution or high-confidence pattern found. Building new solution.'
        }

    def _analyze_and_solve(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze problem and generate baseline solution"""
        context = input_data.get('context', '')
        decision = input_data.get('decision', '')

        # Extract key concepts
        concepts = {
            'has_performance': any(k in context.lower() for k in ['slow', 'optimize', 'performance', 'speed']),
            'has_scale': any(k in context.lower() for k in ['scale', 'growth', 'load', 'traffic']),
            'has_architecture': any(k in context.lower() for k in ['architecture', 'design', 'structure']),
            'has_database': any(k in context.lower() for k in ['database', 'query', 'sql', 'index'])
        }

        recommendations = []

        if concepts['has_performance']:
            recommendations.append({
                'area': 'performance',
                'action': 'Profile code, identify bottlenecks, implement caching',
                'complexity': 'O(1) cache access vs O(n) repeated computation'
            })

        if concepts['has_scale']:
            recommendations.append({
                'area': 'scalability',
                'action': 'Implement horizontal scaling, load balancing, async processing',
                'expected_impact': '10x capacity increase'
            })

        if concepts['has_database']:
            recommendations.append({
                'area': 'database',
                'action': 'Add indexes, optimize queries, consider read replicas',
                'expected_improvement': '3-10x query performance'
            })

        return {
            'analysis': concepts,
            'recommendations': recommendations,
            'immediate_action': recommendations[0] if recommendations else {'action': 'Provide more context for better analysis'}
        }

    def _analyze_future_state(
        self,
        cascades: List[Dict],
        patterns: List[Dict]
    ) -> Dict[str, Any]:
        """Predict future state based on cascade effects"""

        if not cascades:
            return {
                'prediction': 'No cascade data available',
                'confidence': 0.0
            }

        # Group cascades by level
        levels = {}
        for cascade in cascades:
            level = cascade.get('level', 1)
            if level not in levels:
                levels[level] = []
            levels[level].append(cascade)

        # Analyze impact over time
        timeline = []
        for level, effects in sorted(levels.items()):
            timeline.append({
                'timeframe': f'Level {level}',
                'effects': [e.get('effect', {}) for e in effects],
                'probability': sum(e.get('probability', 0) for e in effects) / len(effects) if effects else 0
            })

        return {
            'cascade_depth': len(levels),
            'timeline': timeline,
            'overall_confidence': cascades[0].get('probability', 0.5) if cascades else 0.0,
            'warning': 'Decisions have cascading effects. Consider long-term implications.' if len(levels) > 2 else None
        }

    def _assess_risks(
        self,
        cascades: List[Dict],
        patterns: List[Dict]
    ) -> Dict[str, Any]:
        """Generate risk assessment matrix"""

        risks = []

        # Analyze cascade risks
        for cascade in cascades:
            probability = cascade.get('probability', 0.5)
            if probability < 0.5:
                risks.append({
                    'type': 'cascade_uncertainty',
                    'level': cascade.get('level', 0),
                    'description': f"Low confidence ({probability:.2f}) in prediction",
                    'severity': 'medium'
                })

        # Pattern-based risks
        low_accuracy_patterns = [p for p in patterns if p.get('prediction_accuracy', 0) < 0.6]
        if low_accuracy_patterns:
            risks.append({
                'type': 'pattern_uncertainty',
                'description': f"{len(low_accuracy_patterns)} patterns have low prediction accuracy",
                'severity': 'low',
                'recommendation': 'Validate assumptions manually'
            })

        # Compute overall risk score
        risk_score = len(risks) * 0.2 if risks else 0.1

        return {
            'risk_score': min(risk_score, 1.0),
            'risk_level': 'high' if risk_score > 0.7 else 'medium' if risk_score > 0.4 else 'low',
            'identified_risks': risks,
            'mitigation': 'Test incrementally, monitor metrics, prepare rollback plan' if risks else 'Proceed with confidence'
        }

    def _generate_optimizations(
        self,
        patterns: List[Dict],
        direct_solution: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate optimization suggestions"""

        optimizations = []

        # Extract learned optimizations from high-accuracy patterns
        for pattern in patterns[:3]:  # Top 3 patterns
            if pattern.get('learned_optimization') and pattern.get('prediction_accuracy', 0) > 0.6:
                optimizations.append({
                    'source': f"Pattern: {pattern['pattern_type']}",
                    'optimization': pattern['learned_optimization'],
                    'confidence': f"{pattern['prediction_accuracy']:.0%}",
                    'impact_score': pattern.get('future_impact_score', 0)
                })

        # Add general optimization principles
        if not optimizations:
            optimizations.append({
                'source': 'General principle',
                'optimization': 'Start simple, measure, optimize bottlenecks iteratively',
                'confidence': '100%',
                'note': 'No specific learned patterns yet. System will improve with more interactions.'
            })

        return optimizations

    def _extract_pattern_insights(self, patterns: List[Dict]) -> Dict[str, Any]:
        """Extract insights from matched patterns"""

        if not patterns:
            return {'insight': 'No historical patterns found. This is a new problem space.'}

        top_pattern = patterns[0]

        return {
            'primary_pattern': top_pattern.get('pattern_type'),
            'similarity_score': round(top_pattern.get('similarity_score', 0), 3),
            'historical_occurrences': top_pattern.get('occurrences', 0),
            'prediction_accuracy': round(top_pattern.get('prediction_accuracy', 0), 3),
            'learned_wisdom': top_pattern.get('learned_optimization', 'No optimization recorded'),
            'total_patterns_found': len(patterns)
        }

    def _generate_honest_assessment(
        self,
        input_data: Dict[str, Any],
        solution: Dict[str, Any],
        patterns: List[Dict]
    ) -> Dict[str, str]:
        """Brutally honest assessment of approach and alternatives"""

        assessments = []

        # Assess solution confidence
        confidence = solution.get('confidence', 0.5)
        if confidence < 0.7:
            assessments.append({
                'category': 'Solution Confidence',
                'assessment': f'Current solution confidence is {confidence:.0%}. Not optimal.',
                'action': 'Provide more context or consider alternative approaches.'
            })

        # Assess pattern availability
        if not patterns or len(patterns) < 2:
            assessments.append({
                'category': 'Historical Data',
                'assessment': 'Limited historical patterns available.',
                'action': 'System will learn from this interaction. Future queries will be more accurate.'
            })

        # Assess complexity
        if 'complexity' in input_data:
            assessments.append({
                'category': 'Complexity',
                'assessment': f"Specified complexity: {input_data['complexity']}",
                'action': 'Verify this is optimal. Can you achieve better with different data structures?'
            })

        return {
            'assessments': assessments,
            'bottom_line': 'Solution is viable but may not be optimal. Iterate based on real-world metrics.' if assessments else 'High confidence in solution based on proven patterns.'
        }

    # ========================================================================
    # LEARNING AND ADAPTATION
    # ========================================================================

    async def _learn_from_interaction(
        self,
        input_data: Dict[str, Any],
        response: Dict[str, Any]
    ):
        """Extract patterns and store learned optimizations"""

        # Extract pattern signature
        pattern_type = self._classify_pattern(input_data)

        pattern_signature = {
            'context_type': pattern_type,
            'has_decision': 'decision' in input_data,
            'complexity': input_data.get('complexity', 'unknown')
        }

        # Extract optimization if present
        optimization = None
        if response.get('optimization_path'):
            optimization = json.dumps(response['optimization_path'])

        # Store pattern
        await db.store_pattern(
            pattern_type=pattern_type,
            pattern_signature=pattern_signature,
            learned_optimization=optimization
        )

        # If solution was good, cache it
        if response.get('intelligence_metrics', {}).get('patterns_matched', 0) > 0:
            await db.cache_solution(
                problem_signature={'context': input_data.get('context', '')},
                optimal_solution=response.get('direct_solution', {}),
                performance_metrics=response.get('intelligence_metrics', {})
            )

    def _classify_pattern(self, input_data: Dict[str, Any]) -> str:
        """Classify input into pattern type"""
        context = input_data.get('context', '').lower()

        classifications = {
            'database': ['database', 'query', 'sql', 'index', 'postgres'],
            'performance': ['optimize', 'slow', 'performance', 'speed', 'latency'],
            'architecture': ['architecture', 'design', 'structure', 'pattern'],
            'scaling': ['scale', 'growth', 'load', 'traffic', 'capacity'],
            'caching': ['cache', 'redis', 'memcache', 'cdn'],
            'api': ['api', 'endpoint', 'rest', 'graphql', 'http']
        }

        for pattern_type, keywords in classifications.items():
            if any(keyword in context for keyword in keywords):
                return pattern_type

        return 'general'

    def _add_to_context(self, input_data: Dict[str, Any]):
        """Maintain rolling context window"""
        self.context_window.append({
            'data': input_data,
            'timestamp': datetime.utcnow()
        })

        # Keep only recent context
        if len(self.context_window) > self.max_context_size:
            self.context_window.pop(0)

    # ========================================================================
    # ANALYTICS AND INTROSPECTION
    # ========================================================================

    async def get_system_intelligence(self) -> Dict[str, Any]:
        """Get current system intelligence metrics"""

        metrics = await db.get_intelligence_metrics(hours=24)
        patterns = await db.get_pattern_effectiveness(limit=10)

        return {
            'intelligence_metrics': metrics,
            'top_patterns': patterns,
            'context_window_size': len(self.context_window),
            'learning_rate': self.learning_rate,
            'status': 'Learning and improving with each interaction'
        }


# Global engine instance
engine = IntelligenceEngine()
