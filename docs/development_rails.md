# Development Rails - How to Build Safely Here

## Definition of Done

Every code change must meet these criteria before merge:

### Code Quality Gates
1. **Ruff Clean**: `ruff check .` returns 0 issues on all touched files
2. **Pyright Strict**: `pyright --project .` returns 0 errors on all modified files
3. **Test Non-Regression**: Existing tests continue to pass
4. **Platform Guards Intact**: Windows-specific code properly guarded for Linux development

### Change Documentation
1. **ADR for Breaking Changes**: Architecture changes require Architecture Decision Record
2. **Update Relevant DOCS**: Documentation reflects code changes
3. **Changelog Entry**: User-visible changes documented in CHANGELOG.md

### Validation Commands
```bash
# From repo root: WatchLockAI_Sentinel/
ruff check . --output-format=json > /tmp/ruff.json || true
pyright --project . --outputjson > /tmp/pyright.json || true
pytest -q > /tmp/pytest.txt || true

# Check results match baseline in DOCS/baselines.txt
```

## Commit/Patch Etiquette

### Commit Message Format
```
type(scope): brief description

- Detailed change explanation
- Impact on other components
- Platform-specific considerations

Co-authored-by: MiniMax Agent
```

**Types**: `fix`, `feat`, `refactor`, `docs`, `test`, `chore`  
**Scopes**: `collectors`, `detection`, `response`, `console`, `core`, `config`, `platform`

### File Operation Rules

#### Renames and Moves
- **NEVER rename without ADR**: File renames break imports and require architecture review
- **Move with ADR**: Moving files between packages requires documented decision
- **Update all references**: Grep for old import paths and update systematically

#### Platform Guards
- **Preserve guard patterns**: Don't break conditional imports for Windows-only modules
- **Test on Linux**: Ensure changes work in Linux development environment
- **Document platform assumptions**: Note Windows-only behavior in docstrings

#### Deterministic Operations
- **No randomness**: Use fixed seeds for any random operations
- **Stable sorting**: Always sort collections when order affects behavior
- **Consistent formatting**: Use same formatting tools across team

## Folder Ownership Map

| Module Path | Primary Owner | Secondary Owner | Change Policy |
|---|---|---|---|
| `app_core/` | **Core Infrastructure** | All teams | Requires ADR for breaking changes |
| `collectors/` | **Monitoring Team** | Detection Team | Coordinate schema changes |
| `detection/` | **Security Team** | Monitoring Team | Independent within event contracts |
| `response/` | **Security Team** | Operations Team | Coordinate action capabilities |
| `service/` | **Operations Team** | Core Infrastructure | Service lifecycle changes require ADR |
| `console/` | **UI/API Team** | Security Team | API changes require backward compatibility |
| `config/` | **Operations Team** | All teams | Configuration changes affect all components |
| `ui/` | **UI/API Team** | Operations Team | Independent UI changes |
| `tests/` | **Quality Team** | Feature owners | Test coverage required for changes |
| `DOCS/` | **Documentation Team** | All teams | Keep docs current with code changes |

### Cross-Team Coordination
- **Schema changes**: Require approval from all consuming teams
- **Event bus changes**: Impact all components, require careful rollout
- **Configuration changes**: May require deployment coordination
- **API changes**: Require backward compatibility or versioning strategy

## Small-Batch Refactor Playbook

Follow this sequence for safe refactoring:

### 1. Fix Phase (Isolated)
```bash
# Make the minimal code change
# Focus on single file or closely related files
# Don't rename or move things yet
```

### 2. Validate Phase (Scoped)
```bash
# Run diagnostics on changed files only
ruff check path/to/changed/file.py
pyright path/to/changed/file.py

# Verify specific functionality
python -m pytest tests/related_test.py -v
```

### 3. Integration Phase (Broader)
```bash
# Run full diagnostic suite
ruff check .
pyright --project .
pytest -q

# Compare to baseline counts in DOCS/baselines.txt
```

### 4. Patch Phase (Final)
```bash
# Create patch with proper commit message
git add .
git commit -m "fix(scope): description"

# Update documentation if needed
# Update CHANGELOG.md for user-visible changes
```

### Refactor Patterns

#### Safe Refactors (Low Risk)
- Extract small functions within same module
- Add type hints to existing functions
- Improve error messages and logging
- Add defensive checks and validation
- Split large functions into smaller ones

#### Risky Refactors (High Coordination)
- Change function signatures
- Move code between modules
- Change event schema structure
- Modify configuration structure
- Change API endpoint contracts

## Development Workflow

### Daily Development Cycle
1. **Start**: Check current baseline with `python3 /workspace/compute_master_baselines.py`
2. **Develop**: Make incremental changes following ownership boundaries
3. **Validate**: Run scoped diagnostics on changed components
4. **Test**: Verify functionality with targeted tests
5. **Integrate**: Run full diagnostic suite before commit
6. **Document**: Update relevant DOCS/ files for significant changes

### Code Review Process
1. **Self-Review**: Run full validation suite locally
2. **Peer Review**: Focus on architecture and cross-component impact
3. **Documentation Review**: Ensure DOCS/ reflect code reality
4. **Platform Testing**: Verify Linux compatibility for Windows-specific changes

## Emergency Procedures

### Broken Build Recovery
1. **Identify Scope**: Which diagnostic is failing (ruff, pyright, pytest)?
2. **Isolate Change**: Use git bisect to find breaking commit
3. **Minimal Revert**: Revert smallest possible change to restore build
4. **Root Cause**: Analyze why change broke and improve process

### Platform Compatibility Issues
1. **Linux Development**: Use platform guards to mock Windows-only APIs
2. **Windows Testing**: Test critical paths on actual Windows environment
3. **Guard Failures**: Ensure graceful degradation when platform APIs unavailable

### Dependency Conflicts
1. **Version Pinning**: Lock versions that cause compatibility issues
2. **Optional Dependencies**: Mark non-critical dependencies as optional
3. **Platform Dependencies**: Separate Windows-only dependencies clearly

---

**Document Version**: 1.0  
**Last Updated**: 2025-09-02T20:31:09+00:00  
**Author**: MiniMax Agent