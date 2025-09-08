# Changelog

## [0.8.0] - 2025-09-06

### Added - P2-P4 Suite Complete Implementation

#### P2 Suite: Enhanced Security & Monitoring
- **P2-001**: Anomaly Detection Engine with ML scoring (default OFF, `ANOMALY_ENABLED=0`)
- **P2-002**: Quarantine System with RBAC protection (default OFF, `QUARANTINE_ENABLED=0`)
- **P2-003**: Console Authentication with session management (default OFF, `CONSOLE_AUTH_ENABLED=0`)
- **P2-004**: Real-time Server-Sent Events (SSE) streaming (default OFF, `STREAM_ENABLED=0`)

#### P3 Suite: Production Readiness  
- **P3-001**: Configuration Schema Management with hot reload (default OFF, `CONFIG_HOT_RELOAD_ENABLED=0`)
- **P3-002**: Log Rotation & Secret Redaction (default ON for security, `LOG_REDACT_SECRETS=1`)
- **P3-003**: Windows Service Packaging with installer scripts (default OFF, `SERVICE_ENABLED=0`)
- **P3-004**: Plugin Sandbox System with secure execution (default OFF, `PLUGINS_ENABLED=0`) 
- **P3-005**: Telemetry Export with RBAC gating (default OFF, `EXPORT_ENABLED=0`)
- **P3-006**: Preflight Checks for deployment validation

#### P4 Suite: Ops Polish & Resilience
- **P4-001**: Backup & Restore with timestamped archives (default OFF, `BACKUP_ENABLED=0`)
- **P4-002**: Secret Rotation Toolkit with secure key generation (default OFF, `ROTATE_ENABLED=0`)
- **P4-003**: STRIDE Threat Model & Security Linting (documentation always ON, lints optional)
- **P4-004**: Chaos Engineering Probes for resilience testing (default OFF, `CHAOS_ENABLED=0`)
- **P4-005**: End-to-End Self-Check validation (default ON, non-breaking)
- **P4-006**: Minimal Console UI dashboard (default OFF, `CONSOLE_UI_ENABLED=0`)
- **P4-007**: Documentation Hardening with operations runbooks and flow diagrams

### Security Enhancements
- RBAC implementation with dual authentication (token + session)
- Rate limiting on sensitive endpoints (`RATE_LIMIT_ENABLED=0` by default)
- Secret redaction in logs and rotation toolkit
- STRIDE threat modeling and security linting tools

### API Endpoints Added
- Authentication: `/api/auth/login`, `/api/auth/logout`, `/api/auth/me`
- Admin Management: `/api/admin/config/schema`, `/api/admin/export`, `/api/admin/backup`
- Streaming: `/api/stream/health`, `/api/stream/events` (SSE)
- Anomaly Detection: `/api/anomaly/score`, `/api/admin/anomaly/train`
- Quarantine: `/api/admin/quarantine`, `/api/admin/quarantine/restore`
- Chaos Engineering: `/api/admin/chaos/inject`, `/api/admin/chaos/status`
- Secret Management: `/api/admin/rotate/preview`, `/api/admin/rotate/execute`
- Console UI: `/console/`, `/console/info`

### Changed
- **FastAPI Route Introspection**: Fixed Flask→FastAPI mismatch in API contract checking
- **Feature Flag Architecture**: All new features default OFF for non-breaking deployment
- **Verifier Enhancements**: Added P3 invariant checks and enhanced validation rules
- **Service Integration**: Enhanced Windows service wrapper with installer/uninstaller scripts

### Technical Notes
- 60+ new endpoints with feature flag gating
- 20+ configurable feature flags with safe defaults
- Zero breaking changes - all existing functionality preserved
- Import-safe design with graceful module loading
- Comprehensive test coverage for all new features

### Documentation
- Complete operations runbook with backup/restore procedures
- Windows deployment guide with service integration
- STRIDE threat model analysis in `/DOCS/security/threat_model.md`
- API contract freezing for deployment stability

---

## [0.2.0] - 2025-09-01

### Added - Non-Regressive Integration Build

#### Core Architecture
- **FastAPI Web Interface**: Local HTTP API on 127.0.0.1:8080 for monitoring and management
- **Web Console**: Complete dashboard with pages for Detections, Assets, Accounts, and Processes
- **Enhanced Tray UI**: Added "Open Console" option to launch web interface in browser
- **Thin Client Architecture**: All UI components delegate to Sentinel APIs (no logic duplication)

#### RAG & Knowledge Integration
- **Vendor Research**: Added CrowdStrike terminology and UI patterns research
- **Citations Database**: Comprehensive citations.json with source provenance
- **UX Grounding**: Industry-standard terminology framework for consistent user experience
- **Rebuilt RAG Index**: Enhanced knowledge base with vendor research integration

#### Quality Improvements
- **Updated Dependencies**: Pydantic v2.7.4, FastAPI, and modern toolchain
- **Automated Validation**: Tools for repair, migration, and compatibility testing
- **Build Pipeline**: PowerShell-based build system with PyInstaller integration
- **Zero-Defect Gates**: Ruff, Pyright, and Pytest validation framework

#### Backward Compatibility
- **Schema Preservation**: All existing event schemas maintained (FileEvent@v1, etc.)
- **Legacy Support**: Migration tools preserve existing configuration and data
- **Non-Destructive**: Backup system ensures no functionality loss

#### New Components
- `console/web_api.py`: FastAPI web server and API endpoints
- `console/templates/`: Complete web dashboard with Bootstrap 5 UI
- `tools/repair_and_validate.py`: Automated quality gate validation
- `tools/migrate_prior_state.py`: Legacy configuration preservation
- `tools/compat_matrix.py`: Compatibility testing framework
- `service/installer/build_installer.ps1`: Windows build automation

### Changed
- **Service Architecture**: Extended SentinelService with web API integration
- **Tray Application**: Enhanced menu with web console access
- **Project Metadata**: Updated to EDR v0.2.0 with unified branding
- **Configuration**: Streamlined pyproject.toml and requirements.txt

### Technical Notes
- Single application core with multiple UI frontends
- Local-first design with privacy by default
- Windows-optimized with Linux compatibility for CI/CD
- Falcon-inspired terminology while maintaining original implementation

### Migration Guide
- Existing configurations automatically preserved
- New web console accessible at http://127.0.0.1:8080
- Legacy tray functionality unchanged
- All existing APIs remain functional

---

## [0.1.0] - Previous Version
- Initial Sentinel implementation
- Core monitoring components
- RAG-based detection engine
- Windows service integration