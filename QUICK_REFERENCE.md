# Quick Reference Card - Performance Feedback Loop

## 🎯 Purpose
Collect performance data to enable data-driven optimization decisions (no more guessing!).

## 📊 The Feedback Loop

```
┌─────────────────────────────────────────────────────────────┐
│  1. COLLECT BASELINE                                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ python scripts/collect_performance_data.py \           │ │
│  │   --rps 50 \                                           │ │
│  │   --output baseline.json \                            │ │
│  │   --report baseline.md                                │ │
│  └────────────────────────────────────────────────────────┘ │
│                            ↓                                │
│  2. ANALYZE DATA                                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ cat baseline.md                                        │ │
│  │                                                        │ │
│  │ Look for:                                              │ │
│  │ • High P95 latency (>500ms) → slow queries            │ │
│  │ • High variance (p95/avg >2.5) → connection issues    │ │
│  │ • High errors (>0.1%) → timeouts/failures             │ │
│  └────────────────────────────────────────────────────────┘ │
│                            ↓                                │
│  3. MAKE TARGETED CHANGES                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ # Based on data insights, optimize:                   │ │
│  │ • Database queries (if db_query_duration high)        │ │
│  │ • External calls (if external_request_duration high)  │ │
│  │ • Connection pools (if variance high)                 │ │
│  └────────────────────────────────────────────────────────┘ │
│                            ↓                                │
│  4. MEASURE IMPACT                                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ docker compose up -d --build                          │ │
│  │ python scripts/collect_performance_data.py \           │ │
│  │   --rps 50 \                                           │ │
│  │   --baseline baseline.json \                          │ │
│  │   --output optimized.json \                           │ │
│  │   --report optimized.md                               │ │
│  └────────────────────────────────────────────────────────┘ │
│                            ↓                                │
│  5. VALIDATE RESULTS                                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ cat optimized.md                                       │ │
│  │                                                        │ │
│  │ Check comparison:                                      │ │
│  │ ✓ P95: 450ms → 320ms (-28.89%) ← Good!              │ │
│  │ ✗ Errors: 0% → 2% (+2%) ← Bad, revert!              │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🔑 Key Metrics

| Metric | Good | Warning | Bad | What It Means |
|--------|------|---------|-----|---------------|
| **P95 Latency** | <200ms | 200-500ms | >500ms | 95% of requests complete in this time |
| **Variance (P95/avg)** | <2.0x | 2.0-2.5x | >2.5x | How consistent response times are |
| **Error Rate** | <0.01% | 0.01-0.1% | >0.1% | Percentage of failed requests |

## 🎪 Common Patterns

### Pattern 1: Slow Database Queries
```
Symptoms: High P95, high db_query_duration
Solutions: Add indexes, optimize queries, use connection pooling
```

### Pattern 2: Sequential External Calls
```
Symptoms: High external_request_duration
Solutions: Use asyncio.gather(), add caching, parallelize
```

### Pattern 3: Connection Pool Exhaustion
```
Symptoms: High variance, occasional slow requests
Solutions: Increase pool size, reduce timeouts, add monitoring
```

## 🚀 Quick Commands

```bash
# Start services
docker compose up -d

# Check service health
docker compose ps

# Collect baseline (10 RPS - light load)
python scripts/collect_performance_data.py --rps 10 --output baseline.json --report baseline.md

# After changes, measure impact (50 RPS - normal load)
docker compose up -d --build
python scripts/collect_performance_data.py --rps 50 --baseline baseline.json --output optimized.json --report optimized.md

# View service metrics directly
curl http://localhost:8001/metrics  # heroes
curl http://localhost:8004/metrics  # fights

# Manual quick test
time curl http://localhost:8004/api/fights/randomfighters
```

## 📚 Documentation

| Document | Purpose | Location |
|----------|---------|----------|
| **Quick Start** | Get started fast | `README.md` |
| **Complete Guide** | Full documentation | `docs/PERFORMANCE_FEEDBACK_LOOP.md` |
| **Example** | Step-by-step tutorial | `docs/EXAMPLE_WORKFLOW.md` |
| **AI Instructions** | For AI agents | `.github/copilot/instructions/data-driven-optimization.md` |
| **Implementation** | What we built | `IMPLEMENTATION_SUMMARY.md` |

## 💡 Best Practices

✅ **DO:**
- Always collect baseline before changes
- Test at realistic load (match production RPS)
- Run tests multiple times (3x, take median)
- Include performance data in PRs
- Watch for regressions in other metrics

❌ **DON'T:**
- Optimize without measuring first
- Claim improvements without data
- Test only happy path
- Ignore error rates
- Make changes based on guesses

## 🤖 For AI Agents

When asked to optimize:
1. Run `python scripts/collect_performance_data.py --rps 50 --output baseline.json --report baseline.md`
2. Read `baseline.md` to identify actual bottlenecks
3. Make targeted changes based on data
4. Run collection again with `--baseline baseline.json`
5. Include comparison data in PR with specific percentages

**Never claim performance improvements without data!**

## 📞 Need Help?

- Check `docs/PERFORMANCE_FEEDBACK_LOOP.md` for troubleshooting
- Review `docs/EXAMPLE_WORKFLOW.md` for a complete example
- Read `.github/copilot/instructions/data-driven-optimization.md` for patterns

## 🎯 Success Criteria

Your optimization is successful when:
- ✓ P95 latency reduced by >10%
- ✓ Error rate stays same or improves
- ✓ No regressions in other metrics
- ✓ Results reproducible across 3+ runs
- ✓ Methodology documented in PR

---

**Remember:** Data-driven optimization beats guessing every time! 📊✨
