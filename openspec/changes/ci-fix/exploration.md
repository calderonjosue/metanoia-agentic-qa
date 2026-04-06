# Exploration: CI Failures Diagnosis

## Current State

The CI pipeline is failing with three distinct job failures:

| Job | Status | Root Cause |
|-----|--------|------------|
| Lint (ruff) | FAIL | W293 (whitespace on blank lines), E501 (line too long) |
| Type Check (ruff) | FAIL | Same as Lint - ruff check is run twice |
| Test (pytest) | FAIL | 2 collection errors due to supabase dependency incompatibility |

---

## Affected Areas

| File/Path | Issue | Type |
|-----------|-------|------|
| `src/agents/*.py` | Multiple W293 (trailing whitespace on blank lines) | Code Quality |
| `src/agents/*.py` | Multiple E501 (lines exceeding 88 chars) | Code Quality |
| `src/knowledge/rag.py` | Module-level instantiation causes import failure | Dependency Issue |
| `src/knowledge/client.py` | `ClientOptions` missing `storage` attribute | Dependency Issue |

---

## Root Cause Analysis

### 1. Ruff Lint Errors (W293)

**Error Pattern:** Blank lines contain whitespace characters (spaces/tabs)

**Affected Files (partial list):**
- `src/agents/chaos_agent.py` - 12 occurrences
- `src/agents/chaos_engineer.py` - 15 occurrences  
- `src/agents/context_analyst.py` - 18 occurrences
- `src/agents/design_lead.py` - 25+ occurrences
- `src/agents/performance.py` - 12 occurrences
- `src/agents/security.py` - multiple

**Fix:** `ruff check src/ --fix` (auto-fixes W293)

### 2. Ruff Line Length Errors (E501)

**Error Pattern:** Lines exceeding 88 characters

**Note:** The `pyproject.toml` sets `line-length = 88` for both black and ruff, but ruff is still flagging lines at exactly 88+ characters.

**Example violations:**
```
src/agents/chaos_engineer.py:49:89 - 118 chars
src/agents/chaos_engineer.py:77:89 - 129 chars
src/agents/compliance.py:263:89 - 95 chars
src/agents/design_lead.py:92:89 - 97 chars
```

**Fix Options:**
- Shorten long lines manually
- Update `pyproject.toml` to set `line-length = 100` (more Pythonic)
- Add `E501` to ruff `ignore` list

### 3. Pytest Collection Errors

**Error:** `AttributeError: 'ClientOptions' object has no attribute 'storage'`

**Traceback:**
```
tests/integration/test_shift_right.py → 
src/observability/__init__.py → 
src/knowledge/rag.py:498 (module-level instantiation) →
src/knowledge/client.py:76 →
supabase.create_client() →
supabase/_sync/client.py:285 → 
AttributeError: 'ClientOptions' object has no attribute 'storage'
```

**Root Cause:** 
- Code uses `ClientOptions(auto_refresh_token=True, persist_session=True)`
- Supabase library v2.28.3 expects a `storage` attribute on `ClientOptions`
- This is a **version incompatibility** - likely written for supabase v1.x

**Affected Tests:**
- `tests/integration/test_shift_right.py`
- `tests/knowledge/test_rag.py`

---

## Approaches

### Approach 1: Quick Fix (Skip failing jobs temporarily)

**Pros:** Gets CI green fastest, unblocks other work  
**Cons:** Technical debt accumulates, quality degrades

```yaml
# In CI, conditionally skip:
- if: failure()  # Allow build to proceed even if lint/test fail
```

### Approach 2: Fix Ruff Issues + Isolation (Recommended)

**Pros:** Addresses root issues without major refactoring  
**Cons:** Still leaves supabase compatibility issue for integration tests

1. Run `ruff check src/ --fix` to auto-fix whitespace
2. Add `E501` to ignored rules OR increase line-length to 100
3. Mark integration tests as skippable when supabase unavailable
4. Add `@pytest.mark.integration` to CI with `--ignore` for those tests

### Approach 3: Full Dependency Fix

**Pros:** Proper fix, resolves root cause  
**Cons:** May break other things, requires testing

1. Downgrade supabase to v1.x OR update code for v2.x API
2. Fix all line length issues
3. Ensure all tests pass

---

## Recommendation

**Use Approach 2** for fastest path to green CI:

1. **Auto-fix whitespace:** `ruff check src/ --fix`
2. **Ignore E501** in `pyproject.toml` since line-length is a stylistic choice
3. **Skip integration tests** that require supabase (mark with `@pytest.mark.integration` and use `pytest -m "not integration"` in CI for now)
4. **Track supabase fix** as separate technical debt issue

### Immediate Fix Commands:
```bash
# Auto-fix ruff whitespace issues
ruff check src/ --fix

# Update pyproject.toml to ignore E501
# Add to [tool.ruff.lint]: ignore = ["E501"]

# Run tests excluding integration tests
pytest tests/ -m "not integration" -v
```

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| E501 ignoring masks readability issues | Low | Code review |
| Integration tests never run | Medium | Create follow-up issue to fix supabase |
| Supabase version change breaks runtime | High | Test in dev environment first |

---

## Ready for Proposal

**Yes** - Issues are clearly diagnosed with root causes identified. 

Next step: Create proposal for CI fix workflow that:
1. Auto-fixes ruff issues
2. Properly ignores/skips failing integration tests 
3. Gets build passing while technical debt is tracked
