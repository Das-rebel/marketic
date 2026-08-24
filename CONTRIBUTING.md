# Contributing to Marketic

Thank you for contributing! This guide covers everything you need to know.

## Quick Start

```bash
git clone https://github.com/Das-rebel/marketic
cd marketic
pip install -e .[dev]
python3 init_memory_db.py
python3 examples/marketic_campaign_workflow.py
```

## Development Workflow

### Branching
- `main` — production-ready, always deployable
- Feature branches: `feat/description`
- Fix branches: `fix/description`
- Docs: `docs/description`

### Commits
Follow conventional commits:
```
feat: add VLM ad analysis module
fix: Polymarket base-rate correction
docs: update README with ensemble tiers
test: add budget router margin tests
```

### Testing
```bash
pytest tests/                    # all tests
pytest tests/ -k "budget"        # specific tests
pytest --cov=marketic            # coverage
```

## Architecture Principles

**Strategy brain, not execution clone.**
- Marketic produces briefs + brand kits
- Execution agents (Helena-style) consume them
- We orchestrate existing tools; we don't reimplement

**Brand-as-data.**
- Zero hardcoded brands anywhere
- All templates render via `BrandTokens`
- Tokens sourced from image, memory, or manual entry

**Probability-calibrated signals.**
- Raw volume is drama; `volume × P(YES)` is demand
- Polymarket base rate = 73.4% No resolution
- Every signal source has documented weight rationale

**Audit everything.**
- Every AI call logged: model, cost, confidence, reasoning
- Query via `audit_get_cost_summary()`
- No black-box decisions

## Code Standards

### Python
- Type hints required for public APIs
- Dataclasses for data structures
- Docstrings on all public functions
- Max line length: 100 chars

### MCP Tools
Each tool follows this pattern:
```python
async def handle_tool_name(args):
    # 1. Validate inputs
    # 2. Business logic
    # 3. Audit log the decision
    # 4. Return structured result
```

### Module Structure
```
marketic/
├── module/
│   ├── __init__.py       # exports public API
│   ├── core.py           # main logic
│   └── tests/            # module tests
```

## Adding a New MCP Tool

1. Create handler in `mcp_server.py`:
```python
async def handle_my_tool(args):
    # validate, execute, audit, return
    pass
```

2. Register in `HANDLERS` dict and add to `TOOLS` list.

3. Add to `API_DOCUMENTATION.md`.

4. Write test in `tests/test_my_tool.py`.

## Configuration Philosophy

- All external keys optional
- Graceful degradation when keys missing
- Local-first: Ollama vision, local LLMs preferred
- Free tiers documented (ox-alpha, local Ollama)

## Documentation Standards

- Every feature decision traced to vault source
- Architecture decisions in `docs/FEATURE_GAP_ANALYSIS.md`
- Feature picks in `docs/VAULT_PICKS.md`
- API reference in `API_DOCUMENTATION.md`
- Runnable example in `examples/marketic_campaign_workflow.py`

## Pull Request Checklist

- [ ] Type hints on new public functions
- [ ] Docstrings on new modules/classes
- [ ] Tests for new MCP tools
- [ ] Updated `API_DOCUMENTATION.md` if tool added
- [ ] No hardcoded brands in new code
- [ ] Audit trail calls for AI decisions
- [ ] Example updated if workflow changed

## Getting Help

- GitHub Issues: bugs, features
- Discussions: questions, architecture debates
- Check `docs/FEATURE_GAP_ANALYSIS.md` for design rationale

---

*Built on the principle: strategy brain → brief → execution agent. No black boxes, no hardcoded brands, no reimplementing what MCP servers already provide.*