# Cognitive Memory System

**Database-backed intelligence amplification engine with persistent memory for ChatGPT integration**

## Architecture Overview

This system implements a PostgreSQL-backed persistent memory architecture that:

- **Stores all conversations** with automatic intelligence accumulation
- **Learns from patterns** using Jaccard similarity matching
- **Predicts cascade effects** with recursive depth analysis
- **Caches optimal solutions** for instant retrieval
- **Gets smarter over time** through continuous learning

## Core Components

### 1. Database Layer (`init.sql`)
- **7 tables** for memory, patterns, decisions, optimizations, errors, and code artifacts
- **6 functions** for intelligence accumulation, cascade prediction, pattern similarity
- **2 views** for analytics (intelligence metrics, pattern effectiveness)
- Automatic triggers for intelligence delta calculation

### 2. Connection Layer (`database.py`)
- Async PostgreSQL operations with connection pooling
- CRUD operations for all tables
- Health monitoring and analytics queries
- Error handling and retry logic

### 3. Intelligence Engine (`memory_engine.py`)
- Pattern recognition and classification
- Future state prediction
- Risk assessment matrices
- Optimization generation
- Continuous learning from interactions

### 4. REST API (`api.py`)
- FastAPI with async endpoints
- Interactive documentation at `/docs`
- CORS enabled for web integration
- Comprehensive error handling

## Quick Start

### 1. Deploy with Docker Compose

```bash
cd cognitive-memory
docker-compose up --build -d
```

This starts:
- PostgreSQL on port 5432
- FastAPI on port 8000
- Redis on port 6379

### 2. Verify Deployment

```bash
# Check service health
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs
```

### 3. Process Your First Interaction

```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{
    "context": "optimize database queries with slow performance",
    "decision": "add database indexes",
    "complexity": "O(log n)"
  }'
```

## API Endpoints

### Intelligence Operations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/process` | POST | Process interaction through intelligence engine |
| `/patterns/search` | POST | Search for similar patterns |
| `/patterns/top` | GET | Get most effective patterns |
| `/decisions/analyze` | POST | Analyze decision and predict cascades |
| `/decisions/cascades/{decision}` | GET | Get cascade effects for decision |

### Memory Operations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/memory/history` | GET | Retrieve conversation history |
| `/memory/intelligence-score` | GET | Get intelligence score over time |

### Error Handling

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/errors/log` | POST | Log error with solution |
| `/errors/solution` | POST | Get known solution for error |

### Analytics

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/analytics/intelligence` | GET | Comprehensive intelligence metrics |
| `/analytics/patterns/effectiveness` | GET | Pattern effectiveness analytics |

### System

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System health check |
| `/` | GET | API information |

## Usage Examples

### 1. Basic Intelligence Query

```python
import httpx

response = httpx.post("http://localhost:8000/process", json={
    "context": "implement caching strategy",
    "decision": "use Redis",
    "complexity": "O(1)"
})

result = response.json()
print(result['direct_solution'])
print(result['optimization_path'])
print(result['brutal_honesty'])
```

### 2. Pattern Analysis

```python
response = httpx.post("http://localhost:8000/patterns/search", json={
    "context": {"type": "database_optimization"},
    "similarity_threshold": 0.7,
    "limit": 5
})

patterns = response.json()['patterns']
for pattern in patterns:
    print(f"{pattern['pattern_type']}: {pattern['similarity_score']}")
```

### 3. Decision Cascade Prediction

```python
response = httpx.post("http://localhost:8000/decisions/analyze", json={
    "decision": "migrate to microservices",
    "immediate_impact": {
        "complexity": "high",
        "timeline": "6 months",
        "risk": "medium"
    },
    "confidence_score": 0.75,
    "cascade_depth": 5
})

cascades = response.json()['cascade_effects']
for cascade in cascades:
    print(f"Level {cascade['level']}: {cascade['effect']}")
    print(f"  Probability: {cascade['probability']:.2%}")
```

## Database Schema

### Key Tables

**conversation_memory**
- Stores all interactions with intelligence delta
- Auto-generates context hash
- Tracks causality chains

**pattern_recognition**
- Learns recurring patterns
- Tracks prediction accuracy
- Stores learned optimizations

**decision_cascade**
- Models decision impact chains
- Calculates probability decay
- Validates predictions

**optimization_cache**
- Caches optimal solutions
- Tracks usage frequency
- Measures effectiveness

## Intelligence Accumulation

The system automatically calculates intelligence delta using:

```sql
intelligence_delta = (exact_pattern_matches * 0.15) +
                     (similar_patterns * 0.05) +
                     previous_delta
```

Higher delta = more learning from patterns

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Key variables:
- `DB_PASSWORD`: PostgreSQL password
- `DATABASE_URL`: Full database connection string
- `MAX_CONTEXT_SIZE`: Rolling context window size
- `LEARNING_RATE`: Intelligence learning rate

### Docker Compose Customization

Modify `docker-compose.yml` to:
- Change port mappings
- Adjust resource limits
- Add monitoring services
- Configure networking

## Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
docker-compose logs -f postgres
```

### Database Inspection

```bash
# Connect to PostgreSQL
docker exec -it memory_db psql -U intelligence -d cognitive_state

# View intelligence metrics
SELECT * FROM intelligence_metrics LIMIT 10;

# Check pattern effectiveness
SELECT * FROM pattern_effectiveness LIMIT 10;

# Count total interactions
SELECT COUNT(*) FROM conversation_memory;
```

### Intelligence Metrics

```bash
# Get system intelligence
curl http://localhost:8000/analytics/intelligence?hours=24

# Pattern effectiveness
curl http://localhost:8000/analytics/patterns/effectiveness?limit=20
```

## Integration with ChatGPT

### Custom Instructions

Use this system as ChatGPT's persistent memory:

```markdown
You have access to a cognitive memory database at http://localhost:8000

For every conversation:
1. POST to /process with context and decision
2. Use returned patterns to inform responses
3. Apply learned optimizations
4. Predict future implications
5. Provide brutal honesty assessment

Query patterns before responding:
- POST /patterns/search with context
- Apply top patterns with accuracy > 0.7

Log errors for learning:
- POST /errors/log with context and solution
- Check /errors/solution for known fixes
```

### Next.js Integration

```typescript
// lib/cognitive-memory.ts
const MEMORY_API = 'http://localhost:8000';

export async function processWithMemory(context: string, decision?: string) {
  const response = await fetch(`${MEMORY_API}/process`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ context, decision })
  });

  return response.json();
}

export async function getIntelligenceScore(hours: number = 24) {
  const response = await fetch(
    `${MEMORY_API}/memory/intelligence-score?hours=${hours}`
  );

  return response.json();
}
```

## Maintenance

### Backup Database

```bash
docker exec memory_db pg_dump -U intelligence cognitive_state > backup_$(date +%Y%m%d).sql
```

### Restore Database

```bash
cat backup_20241110.sql | docker exec -i memory_db psql -U intelligence cognitive_state
```

### Cleanup Old Data

```sql
-- Remove interactions older than 90 days
SELECT cleanup_old_data(90);
```

### Rebuild Containers

```bash
docker-compose down
docker-compose up --build -d
```

## Performance Optimization

### Database Indexes

All critical queries are indexed:
- Context hash for O(1) lookups
- GIN indexes on JSONB for pattern matching
- Timestamp indexes for temporal queries

### Connection Pooling

Configured for optimal performance:
- Min pool size: 5
- Max pool size: 20
- Command timeout: 60s

### Caching Strategy

- Redis for hot data (planned)
- PostgreSQL optimization_cache table
- In-memory context window (50 items)

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs

# Verify ports available
lsof -i :5432
lsof -i :8000

# Reset everything
docker-compose down -v
docker-compose up --build
```

### Database Connection Issues

```bash
# Test PostgreSQL connectivity
docker exec -it memory_db psql -U intelligence -d cognitive_state -c "SELECT 1"

# Check environment variables
docker-compose exec app env | grep DATABASE_URL
```

### API Errors

```bash
# Check API health
curl http://localhost:8000/health

# View detailed logs
docker-compose logs -f app

# Restart API service
docker-compose restart app
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     ChatGPT / Next.js App                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI (Port 8000)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Intelligence Engine                                  │   │
│  │  - Pattern Recognition                                │   │
│  │  - Future Prediction                                  │   │
│  │  - Risk Assessment                                    │   │
│  │  - Optimization Generation                            │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ AsyncPG
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL 15 (Port 5432)                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ conversation_memory     │ pattern_recognition        │   │
│  │ decision_cascade        │ optimization_cache         │   │
│  │ error_registry          │ code_artifacts             │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Functions: accumulate_intelligence(), predict_cascade│   │
│  │           find_similar_patterns()                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Philosophy

**Code > Analysis > Alternatives**

This system embodies:
- **No fluff**: Direct solutions with brutal honesty
- **Future-thinking**: Predict cascade effects proactively
- **Continuous learning**: Gets smarter with every interaction
- **Persistent memory**: Never forgets patterns or solutions
- **Evidence-based**: All suggestions backed by historical data

## License

MIT License - See LICENSE file for details

## Contributing

This is a technical system. Contributions should:
1. Be code-first (implementation > documentation)
2. Include performance benchmarks
3. Add tests for new features
4. Maintain < 100ms p95 latency

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Review API docs: `http://localhost:8000/docs`
3. Test health endpoint: `http://localhost:8000/health`
4. Check database connectivity
