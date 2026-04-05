# Proposal: Test Strategy Automation

## Intent

Automate test prioritization, ROI calculation, and metrics collection for Metanoia-QA to enable risk-based test selection and data-driven quality decisions. Currently, test selection is manual and inconsistent; this change provides algorithmic prioritization integrated with StrategyManager.

## Scope

### In Scope
- **Priority Matrix**: 2×2 quadrant (Impact × Severity) with weighted scoring (60% severity, 40% impact)
- **ROI Calculator**: Manual vs automated cost comparison, break-even analysis, coverage gain calculation
- **Severity/Impact Engine**: P0-P4 scale, business impact correlation, configurable risk tolerance
- **Metrics Collection**: MTTD, MTTR, Coverage %, Defect Escape Rate with trend tracking
- **Test Selection Optimizer**: Change-impact analysis, risk-based selection, minimal viable test suite
- **StrategyManager Integration**: Priority signals to agent for test execution ordering

### Out of Scope
- Full Jira integration (deferred to future enhancement)
- Complex ML-based prediction models (Phase 4 may revisit)
- Exploratory testing coordination (separate initiative)

## Approach

**Phase 1 (Weeks 1-4)**: Build Priority Matrix engine with weighted scoring and Severity/Impact definitions. Integrate priority signals into StrategyManager.

**Phase 2 (Weeks 5-8)**: Implement ROI Calculator (manual vs automated cost model) and Test Selection Optimizer using change-impact analysis with risk-based ranking.

**Phase 3 (Weeks 9-12)**: Metrics Dashboard with MTTD/MTTR/Coverage/Escape Rate tracking, trend visualization, and threshold alerting.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/agents/StrategyManager.ts` | Modified | Receives priority signals, orders test execution |
| `src/core/priority-matrix.ts` | New | 2×2 quadrant scoring engine |
| `src/core/roi-calculator.ts` | New | Cost modeling and break-even analysis |
| `src/core/severity-impact.ts` | New | P0-P4 definitions and risk tolerance config |
| `src/core/test-selector.ts` | New | Change-impact analysis and test ranking |
| `src/dashboards/metrics.ts` | New | Metrics collection and trend tracking |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Priority gaming by developers | Medium | Multi-signal validation (severity + impact + history) |
| ROI model inaccurate for org | Medium | Configurable cost parameters with calibration period |
| Over-automation of low-value tests | Medium | Mandatory ROI validation before adding tests |

## Rollback Plan

Disable feature flags for each module independently. Priority Matrix and Severity Engine store original priority in `test.priorityLegacy` field. ROI Calculator calculations are read-only snapshots. Rollback is staged by phase.

## Dependencies

- StrategyManager agent must expose `selectTests(priorityMatrix)` interface
- Metrics store must exist for dashboard (use existing logging infrastructure)

## Success Criteria

- [ ] Priority Matrix assigns scores 1-10 within 5% of expected quadrant boundaries
- [ ] ROI Calculator break-even accuracy within 10% of actual costs (calibrated quarterly)
- [ ] Test Selection reduces regression suite by ≥30% while maintaining ≥80% coverage of changed code
- [ ] Metrics Dashboard displays MTTD/MTTR with ≤1 hour data lag
- [ ] StrategyManager integration adds <100ms latency to test selection decisions
