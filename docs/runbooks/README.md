# Available Runbooks

This directory contains operational runbooks for common maintenance and troubleshooting tasks.

## Core Runbooks

### Development & Setup
- [Session Startup Guide](../session_startup.md) - Environment setup and component testing
- [Development Rails](../development_rails.md) - Safe development workflow and Definition of Done

### Quality Assurance
- [Testing Strategy](../testing_strategy.md) - Test execution and validation procedures
- [Release Checklist](../release_checklist.md) - Pre-deployment validation steps

### Architecture & Planning
- [Architecture Overview](../architecture.md) - System design and component interactions
- [Master Task List](../master_todo.md) - Prioritized development backlog

## Quick Reference Links

| Runbook | Purpose | Frequency | Estimated Time |
|---|---|---|---|
| [Session Startup](../session_startup.md) | Daily dev environment setup | Daily | 5-10 minutes |
| [Smoke Tests](../testing_strategy.md#smoke-test-recipe) | Quick system validation | After changes | 2-5 minutes |
| [Baseline Validation](../development_rails.md#definition-of-done) | Code quality gates | Before commit | 3-5 minutes |
| [Release Validation](../release_checklist.md) | Pre-deployment checks | Per release | 15-30 minutes |

## Emergency Procedures

### Platform Compatibility Issues
- **Windows modules missing on Linux**: See [Session Startup - Platform Guard Notes](../session_startup.md#platform-guard-notes)
- **Service won't start**: See [Session Startup - Troubleshooting](../session_startup.md#troubleshooting-table)
- **Import errors**: Check platform guards in [Development Rails](../development_rails.md#platform-guards-and-type-safety)

### Build Failures
- **Ruff/Pyright errors**: Follow [Development Rails - Small-Batch Refactor](../development_rails.md#small-batch-refactor-playbook)
- **Test failures**: See [Testing Strategy - CI Invariants](../testing_strategy.md#ci-invariants)
- **Broken baseline**: Use [Development Rails - Emergency Procedures](../development_rails.md#emergency-procedures)

## Usage Examples

### Starting a Development Session
```bash
# Follow session startup runbook
cd /workspace/WatchLockAI_Sentinel
source .venv/bin/activate
python3 /workspace/compute_master_baselines.py
./DOCS/smoke_test.sh
```

### Before Making Changes
```bash
# Check current state
ruff check .
pyright --project .
pytest -q
```

### Before Committing
```bash
# Validate changes
./DOCS/pre_release_validation.sh
git add .
git commit -m "fix(scope): description"
```

---

**Document Version**: 1.0  
**Last Updated**: 2025-09-02T20:31:09+00:00  
**Author**: MiniMax Agent