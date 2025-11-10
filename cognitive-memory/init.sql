-- Cognitive Memory Database Initialization
-- Persistent Intelligence Schema for ChatGPT Memory Integration

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- CORE MEMORY TABLE: Stores all conversation interactions
-- ============================================================================
CREATE TABLE conversation_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    context_hash VARCHAR(64),
    interaction JSONB NOT NULL,
    future_implications JSONB DEFAULT '[]'::jsonb,
    causality_chain TEXT[] DEFAULT ARRAY[]::TEXT[],
    intelligence_delta FLOAT DEFAULT 0.0,
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Performance indexes
    CONSTRAINT interaction_not_empty CHECK (jsonb_typeof(interaction) = 'object')
);

-- Auto-generate context hash from interaction
CREATE OR REPLACE FUNCTION generate_context_hash()
RETURNS TRIGGER AS $$
BEGIN
    NEW.context_hash := encode(sha256(NEW.interaction::text::bytea), 'hex');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_generate_context_hash
BEFORE INSERT OR UPDATE ON conversation_memory
FOR EACH ROW EXECUTE FUNCTION generate_context_hash();

-- ============================================================================
-- PATTERN RECOGNITION SYSTEM: Learns from conversation patterns
-- ============================================================================
CREATE TABLE pattern_recognition (
    pattern_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_type VARCHAR(100) NOT NULL,
    pattern_signature JSONB NOT NULL,
    occurrences INT DEFAULT 1,
    prediction_accuracy FLOAT DEFAULT 0.5,
    future_impact_score FLOAT DEFAULT 0.0,
    learned_optimization TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_seen TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT accuracy_range CHECK (prediction_accuracy BETWEEN 0 AND 1),
    CONSTRAINT impact_positive CHECK (future_impact_score >= 0)
);

-- ============================================================================
-- DECISION CASCADE TRACKING: Predicts nth-order effects
-- ============================================================================
CREATE TABLE decision_cascade (
    decision_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision TEXT NOT NULL,
    immediate_impact JSONB DEFAULT '{}'::jsonb,
    cascade_effects JSONB[] DEFAULT ARRAY[]::jsonb[],
    probability_matrix FLOAT[][] DEFAULT ARRAY[]::FLOAT[][],
    confidence_score FLOAT DEFAULT 0.5,
    validated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT confidence_range CHECK (confidence_score BETWEEN 0 AND 1)
);

-- ============================================================================
-- OPTIMIZATION CACHE: Stores proven optimal solutions
-- ============================================================================
CREATE TABLE optimization_cache (
    cache_key VARCHAR(64) PRIMARY KEY,
    problem_signature JSONB NOT NULL,
    optimal_solution JSONB NOT NULL,
    performance_metrics JSONB DEFAULT '{}'::jsonb,
    usage_count INT DEFAULT 0,
    last_accessed TIMESTAMPTZ DEFAULT NOW(),
    effectiveness_score FLOAT DEFAULT 0.5
);

-- ============================================================================
-- ERROR REGISTRY: Tracks errors and their solutions
-- ============================================================================
CREATE TABLE error_registry (
    error_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    error_signature VARCHAR(64) NOT NULL,
    error_context JSONB NOT NULL,
    solution JSONB,
    occurrence_count INT DEFAULT 1,
    resolution_time_seconds INT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_occurred TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- CODE ARTIFACTS: Stores generated code with performance metrics
-- ============================================================================
CREATE TABLE code_artifacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversation_memory(id) ON DELETE CASCADE,
    code TEXT NOT NULL,
    language VARCHAR(50) NOT NULL,
    performance_metrics JSONB DEFAULT '{}'::jsonb,
    optimization_potential FLOAT DEFAULT 0.0,
    complexity_class VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- PERFORMANCE INDEXES
-- ============================================================================
CREATE INDEX idx_memory_timestamp ON conversation_memory(timestamp DESC);
CREATE INDEX idx_memory_context ON conversation_memory(context_hash);
CREATE INDEX idx_memory_interaction_gin ON conversation_memory USING gin(interaction);
CREATE INDEX idx_pattern_type ON pattern_recognition(pattern_type);
CREATE INDEX idx_pattern_accuracy ON pattern_recognition(prediction_accuracy DESC);
CREATE INDEX idx_pattern_signature_gin ON pattern_recognition USING gin(pattern_signature);
CREATE INDEX idx_cascade_confidence ON decision_cascade(confidence_score DESC);
CREATE INDEX idx_cascade_created ON decision_cascade(created_at DESC);
CREATE INDEX idx_optimization_effectiveness ON optimization_cache(effectiveness_score DESC);
CREATE INDEX idx_error_signature ON error_registry(error_signature);

-- ============================================================================
-- INTELLIGENCE ACCUMULATION TRIGGER
-- ============================================================================
CREATE OR REPLACE FUNCTION accumulate_intelligence()
RETURNS TRIGGER AS $$
DECLARE
    pattern_count INT;
    new_delta FLOAT;
    similar_patterns INT;
BEGIN
    -- Count exact pattern matches
    SELECT COUNT(*) INTO pattern_count
    FROM pattern_recognition
    WHERE pattern_signature @> NEW.interaction;

    -- Count similar patterns (fuzzy match on keys)
    SELECT COUNT(*) INTO similar_patterns
    FROM pattern_recognition
    WHERE pattern_signature ?| ARRAY(SELECT jsonb_object_keys(NEW.interaction));

    -- Calculate intelligence delta
    new_delta := (pattern_count * 0.15) + (similar_patterns * 0.05) + COALESCE(NEW.intelligence_delta, 0);

    NEW.intelligence_delta := LEAST(new_delta, 100.0); -- Cap at 100

    -- Update related patterns
    UPDATE pattern_recognition
    SET occurrences = occurrences + 1,
        last_seen = NOW(),
        prediction_accuracy = LEAST(prediction_accuracy + 0.02, 1.0),
        future_impact_score = future_impact_score + 0.1
    WHERE pattern_signature @> NEW.interaction;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_accumulate_intelligence
BEFORE INSERT ON conversation_memory
FOR EACH ROW EXECUTE FUNCTION accumulate_intelligence();

-- ============================================================================
-- CASCADE EFFECT PREDICTION FUNCTION
-- ============================================================================
CREATE OR REPLACE FUNCTION predict_cascade(
    input_decision TEXT,
    depth INT DEFAULT 5
)
RETURNS TABLE(
    level INT,
    effect JSONB,
    probability FLOAT,
    cumulative_confidence FLOAT
) AS $$
BEGIN
    RETURN QUERY
    WITH RECURSIVE cascade AS (
        -- Base case: find direct impacts
        SELECT
            1 as level,
            immediate_impact as effect,
            confidence_score as probability,
            confidence_score as cumulative_confidence
        FROM decision_cascade
        WHERE decision ILIKE '%' || input_decision || '%'
        ORDER BY confidence_score DESC
        LIMIT 1

        UNION ALL

        -- Recursive case: chain effects
        SELECT
            c.level + 1,
            dc.immediate_impact,
            dc.confidence_score,
            c.cumulative_confidence * dc.confidence_score
        FROM cascade c
        JOIN decision_cascade dc ON dc.decision::text = c.effect->>'next_action'
        WHERE c.level < depth
          AND c.cumulative_confidence > 0.1 -- Prune low probability branches
    )
    SELECT * FROM cascade
    ORDER BY level, probability DESC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- PATTERN SIMILARITY SEARCH FUNCTION
-- ============================================================================
CREATE OR REPLACE FUNCTION find_similar_patterns(
    input_context JSONB,
    similarity_threshold FLOAT DEFAULT 0.7
)
RETURNS TABLE(
    pattern_id UUID,
    pattern_type VARCHAR,
    similarity_score FLOAT,
    learned_optimization TEXT,
    prediction_accuracy FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        pr.pattern_id,
        pr.pattern_type,
        -- Calculate Jaccard similarity
        (
            SELECT COUNT(*)::FLOAT / NULLIF(
                (SELECT COUNT(*) FROM jsonb_object_keys(pr.pattern_signature)) +
                (SELECT COUNT(*) FROM jsonb_object_keys(input_context)) -
                COUNT(*), 0
            )
            FROM (
                SELECT jsonb_object_keys(pr.pattern_signature)
                INTERSECT
                SELECT jsonb_object_keys(input_context)
            ) AS intersection
        ) as similarity_score,
        pr.learned_optimization,
        pr.prediction_accuracy
    FROM pattern_recognition pr
    WHERE pr.prediction_accuracy > 0.3
    HAVING (
        SELECT COUNT(*)::FLOAT / NULLIF(
            (SELECT COUNT(*) FROM jsonb_object_keys(pr.pattern_signature)) +
            (SELECT COUNT(*) FROM jsonb_object_keys(input_context)) -
            COUNT(*), 0
        )
        FROM (
            SELECT jsonb_object_keys(pr.pattern_signature)
            INTERSECT
            SELECT jsonb_object_keys(input_context)
        ) AS intersection
    ) >= similarity_threshold
    ORDER BY similarity_score DESC, prediction_accuracy DESC
    LIMIT 10;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- INTELLIGENT RESPONSE GENERATION FUNCTION
-- ============================================================================
CREATE OR REPLACE FUNCTION generate_intelligent_response(
    user_input JSONB,
    context_depth INT DEFAULT 5
)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
    patterns JSONB;
    cascades JSONB;
    intelligence_score FLOAT;
BEGIN
    -- Find relevant patterns
    SELECT jsonb_agg(row_to_json(t))
    INTO patterns
    FROM find_similar_patterns(user_input) t;

    -- Get recent intelligence delta average
    SELECT COALESCE(AVG(intelligence_delta), 0)
    INTO intelligence_score
    FROM conversation_memory
    WHERE timestamp > NOW() - INTERVAL '1 hour';

    -- Build response
    result := jsonb_build_object(
        'patterns', COALESCE(patterns, '[]'::jsonb),
        'intelligence_score', intelligence_score,
        'context_depth', context_depth,
        'timestamp', NOW()
    );

    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- ANALYTICS VIEWS
-- ============================================================================
CREATE VIEW intelligence_metrics AS
SELECT
    DATE_TRUNC('hour', timestamp) as hour,
    COUNT(*) as interactions,
    AVG(intelligence_delta) as avg_intelligence_gain,
    MAX(intelligence_delta) as max_intelligence_gain,
    COUNT(DISTINCT context_hash) as unique_contexts
FROM conversation_memory
GROUP BY DATE_TRUNC('hour', timestamp)
ORDER BY hour DESC;

CREATE VIEW pattern_effectiveness AS
SELECT
    pattern_type,
    occurrences,
    prediction_accuracy,
    future_impact_score,
    EXTRACT(EPOCH FROM (last_seen - created_at)) / 3600 as hours_active,
    occurrences::FLOAT / NULLIF(EXTRACT(EPOCH FROM (last_seen - created_at)) / 3600, 0) as occurrences_per_hour
FROM pattern_recognition
WHERE occurrences > 1
ORDER BY prediction_accuracy DESC, occurrences DESC;

-- ============================================================================
-- SAMPLE DATA FOR TESTING
-- ============================================================================
INSERT INTO conversation_memory (interaction, future_implications) VALUES
(
    '{"context": "optimize database query", "decision": "add index", "complexity": "O(log n)"}'::jsonb,
    '[{"level": 1, "effect": "query performance improves", "probability": 0.9}, {"level": 2, "effect": "reduced server load", "probability": 0.8}]'::jsonb
),
(
    '{"context": "implement caching", "decision": "use redis", "complexity": "O(1)"}'::jsonb,
    '[{"level": 1, "effect": "faster response times", "probability": 0.95}, {"level": 2, "effect": "reduced database queries", "probability": 0.9}]'::jsonb
);

INSERT INTO pattern_recognition (pattern_type, pattern_signature, learned_optimization) VALUES
(
    'database_optimization',
    '{"context": "optimize database query", "solution_type": "indexing"}'::jsonb,
    'Always analyze query execution plan before adding indexes. Consider composite indexes for multi-column WHERE clauses.'
),
(
    'caching_strategy',
    '{"context": "implement caching", "technology": "redis"}'::jsonb,
    'Use cache-aside pattern with TTL. Invalidate cache on writes. Consider cache warming for frequently accessed data.'
);

INSERT INTO decision_cascade (decision, immediate_impact, confidence_score) VALUES
(
    'add database index',
    '{"performance_gain": "3x faster queries", "storage_impact": "+50MB", "maintenance_cost": "low"}'::jsonb,
    0.92
),
(
    'implement redis caching',
    '{"performance_gain": "10x faster reads", "complexity": "medium", "infrastructure_cost": "moderate"}'::jsonb,
    0.88
);

-- ============================================================================
-- MAINTENANCE FUNCTIONS
-- ============================================================================
CREATE OR REPLACE FUNCTION cleanup_old_data(days_to_keep INT DEFAULT 90)
RETURNS INT AS $$
DECLARE
    deleted_count INT;
BEGIN
    WITH deleted AS (
        DELETE FROM conversation_memory
        WHERE timestamp < NOW() - (days_to_keep || ' days')::INTERVAL
        RETURNING *
    )
    SELECT COUNT(*) INTO deleted_count FROM deleted;

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE '============================================================================';
    RAISE NOTICE 'Cognitive Memory Database Initialized Successfully';
    RAISE NOTICE '============================================================================';
    RAISE NOTICE 'Tables created: 7';
    RAISE NOTICE 'Functions created: 6';
    RAISE NOTICE 'Views created: 2';
    RAISE NOTICE 'Sample data inserted: Yes';
    RAISE NOTICE '============================================================================';
END $$;
