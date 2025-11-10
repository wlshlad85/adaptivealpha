"""
Database Connection Layer - Async PostgreSQL Operations
Handles all database interactions with connection pooling and error handling
"""

import os
import asyncpg
from contextlib import asynccontextmanager
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib


class CognitiveDatabase:
    """
    High-performance database interface with connection pooling
    Provides async methods for all cognitive memory operations
    """

    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.db_url = os.getenv(
            'DATABASE_URL',
            'postgresql://intelligence:neural_network_2024@postgres:5432/cognitive_state'
        )

    async def init_pool(self):
        """Initialize connection pool with optimized settings"""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                self.db_url,
                min_size=5,
                max_size=20,
                command_timeout=60,
                max_queries=50000,
                max_inactive_connection_lifetime=300
            )
            print(f"✓ Database pool initialized: {self.db_url.split('@')[1]}")

    async def close_pool(self):
        """Gracefully close all database connections"""
        if self.pool:
            await self.pool.close()
            print("✓ Database pool closed")

    @asynccontextmanager
    async def acquire(self):
        """Context manager for acquiring database connections"""
        if not self.pool:
            await self.init_pool()

        async with self.pool.acquire() as conn:
            yield conn

    # ========================================================================
    # CONVERSATION MEMORY OPERATIONS
    # ========================================================================

    async def store_interaction(
        self,
        interaction: Dict[str, Any],
        future_implications: Optional[List[Dict]] = None,
        causality_chain: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Store conversation interaction with intelligence accumulation
        Returns: {id, intelligence_delta, timestamp}
        """
        async with self.acquire() as conn:
            result = await conn.fetchrow("""
                INSERT INTO conversation_memory (
                    interaction,
                    future_implications,
                    causality_chain,
                    metadata
                )
                VALUES ($1, $2, $3, $4)
                RETURNING id, intelligence_delta, timestamp, context_hash
            """,
                json.dumps(interaction),
                json.dumps(future_implications or []),
                causality_chain or [],
                json.dumps({
                    'source': 'api',
                    'version': '1.0',
                    'stored_at': datetime.utcnow().isoformat()
                })
            )

            return dict(result)

    async def retrieve_context(
        self,
        context_hash: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict]:
        """Retrieve conversation history with optional filtering"""
        async with self.acquire() as conn:
            query = """
                SELECT
                    id,
                    timestamp,
                    context_hash,
                    interaction,
                    future_implications,
                    intelligence_delta
                FROM conversation_memory
            """

            if context_hash:
                query += " WHERE context_hash = $1"
                query += " ORDER BY timestamp DESC LIMIT $2 OFFSET $3"
                rows = await conn.fetch(query, context_hash, limit, offset)
            else:
                query += " ORDER BY timestamp DESC LIMIT $1 OFFSET $2"
                rows = await conn.fetch(query, limit, offset)

            return [dict(row) for row in rows]

    async def get_intelligence_score(self, hours: int = 1) -> float:
        """Calculate average intelligence gain over specified time period"""
        async with self.acquire() as conn:
            result = await conn.fetchval("""
                SELECT COALESCE(AVG(intelligence_delta), 0)
                FROM conversation_memory
                WHERE timestamp > NOW() - INTERVAL '%s hours'
            """ % hours)

            return float(result)

    # ========================================================================
    # PATTERN RECOGNITION OPERATIONS
    # ========================================================================

    async def find_patterns(
        self,
        context: Dict[str, Any],
        similarity_threshold: float = 0.7
    ) -> List[Dict]:
        """
        Find similar patterns using PostgreSQL function
        Uses Jaccard similarity for pattern matching
        """
        async with self.acquire() as conn:
            patterns = await conn.fetch("""
                SELECT * FROM find_similar_patterns($1, $2)
            """, json.dumps(context), similarity_threshold)

            return [dict(p) for p in patterns]

    async def store_pattern(
        self,
        pattern_type: str,
        pattern_signature: Dict[str, Any],
        learned_optimization: Optional[str] = None
    ) -> str:
        """
        Store or update a recognized pattern
        Automatically increments occurrence count
        """
        async with self.acquire() as conn:
            result = await conn.fetchval("""
                INSERT INTO pattern_recognition (
                    pattern_type,
                    pattern_signature,
                    learned_optimization
                )
                VALUES ($1, $2, $3)
                ON CONFLICT (pattern_id) DO UPDATE SET
                    occurrences = pattern_recognition.occurrences + 1,
                    learned_optimization = COALESCE(EXCLUDED.learned_optimization, pattern_recognition.learned_optimization),
                    last_seen = NOW()
                RETURNING pattern_id
            """, pattern_type, json.dumps(pattern_signature), learned_optimization)

            return str(result)

    async def get_top_patterns(
        self,
        limit: int = 10,
        min_accuracy: float = 0.5
    ) -> List[Dict]:
        """Retrieve most effective patterns"""
        async with self.acquire() as conn:
            patterns = await conn.fetch("""
                SELECT
                    pattern_type,
                    pattern_signature,
                    occurrences,
                    prediction_accuracy,
                    future_impact_score,
                    learned_optimization
                FROM pattern_recognition
                WHERE prediction_accuracy >= $1
                ORDER BY prediction_accuracy DESC, occurrences DESC
                LIMIT $2
            """, min_accuracy, limit)

            return [dict(p) for p in patterns]

    # ========================================================================
    # DECISION CASCADE OPERATIONS
    # ========================================================================

    async def predict_cascade_effects(
        self,
        decision: str,
        depth: int = 5
    ) -> List[Dict]:
        """
        Predict nth-order effects of a decision
        Returns cascade chain with probability decay
        """
        async with self.acquire() as conn:
            effects = await conn.fetch("""
                SELECT
                    level,
                    effect,
                    probability,
                    cumulative_confidence
                FROM predict_cascade($1, $2)
            """, decision, depth)

            return [dict(e) for e in effects]

    async def store_decision(
        self,
        decision: str,
        immediate_impact: Dict[str, Any],
        cascade_effects: Optional[List[Dict]] = None,
        confidence_score: float = 0.5
    ) -> str:
        """Store decision with predicted impacts"""
        async with self.acquire() as conn:
            result = await conn.fetchval("""
                INSERT INTO decision_cascade (
                    decision,
                    immediate_impact,
                    cascade_effects,
                    confidence_score
                )
                VALUES ($1, $2, $3, $4)
                RETURNING decision_id
            """,
                decision,
                json.dumps(immediate_impact),
                [json.dumps(e) for e in (cascade_effects or [])],
                confidence_score
            )

            return str(result)

    # ========================================================================
    # OPTIMIZATION CACHE OPERATIONS
    # ========================================================================

    async def get_cached_solution(
        self,
        problem_signature: Dict[str, Any]
    ) -> Optional[Dict]:
        """Retrieve cached optimal solution if available"""
        cache_key = hashlib.sha256(
            json.dumps(problem_signature, sort_keys=True).encode()
        ).hexdigest()

        async with self.acquire() as conn:
            result = await conn.fetchrow("""
                UPDATE optimization_cache
                SET usage_count = usage_count + 1,
                    last_accessed = NOW()
                WHERE cache_key = $1
                RETURNING optimal_solution, performance_metrics, effectiveness_score
            """, cache_key)

            return dict(result) if result else None

    async def cache_solution(
        self,
        problem_signature: Dict[str, Any],
        optimal_solution: Dict[str, Any],
        performance_metrics: Optional[Dict] = None
    ) -> str:
        """Cache an optimal solution for future use"""
        cache_key = hashlib.sha256(
            json.dumps(problem_signature, sort_keys=True).encode()
        ).hexdigest()

        async with self.acquire() as conn:
            await conn.execute("""
                INSERT INTO optimization_cache (
                    cache_key,
                    problem_signature,
                    optimal_solution,
                    performance_metrics
                )
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (cache_key) DO UPDATE SET
                    optimal_solution = EXCLUDED.optimal_solution,
                    performance_metrics = EXCLUDED.performance_metrics,
                    usage_count = optimization_cache.usage_count + 1,
                    last_accessed = NOW()
            """,
                cache_key,
                json.dumps(problem_signature),
                json.dumps(optimal_solution),
                json.dumps(performance_metrics or {})
            )

            return cache_key

    # ========================================================================
    # ERROR TRACKING OPERATIONS
    # ========================================================================

    async def log_error(
        self,
        error_context: Dict[str, Any],
        solution: Optional[Dict[str, Any]] = None,
        resolution_time: Optional[int] = None
    ) -> str:
        """Log error with optional solution"""
        error_signature = hashlib.sha256(
            json.dumps(error_context, sort_keys=True).encode()
        ).hexdigest()

        async with self.acquire() as conn:
            result = await conn.fetchval("""
                INSERT INTO error_registry (
                    error_signature,
                    error_context,
                    solution,
                    resolution_time_seconds
                )
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (error_signature) DO UPDATE SET
                    occurrence_count = error_registry.occurrence_count + 1,
                    solution = COALESCE(EXCLUDED.solution, error_registry.solution),
                    last_occurred = NOW()
                RETURNING error_id
            """,
                error_signature,
                json.dumps(error_context),
                json.dumps(solution) if solution else None,
                resolution_time
            )

            return str(result)

    async def get_error_solution(self, error_context: Dict[str, Any]) -> Optional[Dict]:
        """Retrieve known solution for similar error"""
        error_signature = hashlib.sha256(
            json.dumps(error_context, sort_keys=True).encode()
        ).hexdigest()

        async with self.acquire() as conn:
            result = await conn.fetchrow("""
                SELECT solution, occurrence_count, resolution_time_seconds
                FROM error_registry
                WHERE error_signature = $1
                  AND solution IS NOT NULL
            """, error_signature)

            return dict(result) if result else None

    # ========================================================================
    # ANALYTICS AND METRICS
    # ========================================================================

    async def get_intelligence_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Retrieve system intelligence metrics"""
        async with self.acquire() as conn:
            result = await conn.fetchrow("""
                SELECT
                    COUNT(*) as total_interactions,
                    AVG(intelligence_delta) as avg_intelligence_gain,
                    MAX(intelligence_delta) as max_intelligence_gain,
                    COUNT(DISTINCT context_hash) as unique_contexts,
                    SUM(intelligence_delta) as total_intelligence_accumulated
                FROM conversation_memory
                WHERE timestamp > NOW() - INTERVAL '%s hours'
            """ % hours)

            return dict(result)

    async def get_pattern_effectiveness(self, limit: int = 20) -> List[Dict]:
        """Retrieve pattern effectiveness analytics"""
        async with self.acquire() as conn:
            patterns = await conn.fetch("""
                SELECT * FROM pattern_effectiveness
                LIMIT $1
            """, limit)

            return [dict(p) for p in patterns]

    async def health_check(self) -> Dict[str, Any]:
        """Verify database connectivity and performance"""
        try:
            async with self.acquire() as conn:
                version = await conn.fetchval("SELECT version()")
                uptime = await conn.fetchval("SELECT NOW() - pg_postmaster_start_time()")
                connections = await conn.fetchval("SELECT count(*) FROM pg_stat_activity")

                return {
                    'status': 'healthy',
                    'version': version.split()[1],
                    'uptime_seconds': uptime.total_seconds(),
                    'active_connections': connections,
                    'pool_size': self.pool.get_size() if self.pool else 0
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }


# Global database instance
db = CognitiveDatabase()
