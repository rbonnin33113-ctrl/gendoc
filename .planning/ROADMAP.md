# Roadmap: Generateur de Fiches Techniques Delagrave — v1.6 Deploiement Multi-Postes

## Milestone Goal

Rendre le systeme deployable sur des postes PC utilisant Claude CLI, avec donnees partagees en lecture seule sur un lecteur reseau et output utilisateur local par devis.

**Started:** 2026-02-16
**Status:** In Progress
**Phases:** 22-26 (5 phases)
**Depth:** Standard

## Phases

- [x] **Phase 22: Configuration and Path Resolution** - Read config, resolve all paths from network share (completed 2026-02-16)
- [ ] **Phase 23: Output Restructuring** - Isolate output per devis in user working directory
- [ ] **Phase 24: Access Control** - Admin flag and CRUD restrictions
- [ ] **Phase 25: Deployment Package** - Package, MCP config, deployment guide
- [ ] **Phase 26: Testing and Validation** - Full test suite with config and admin tests

## Phase Details

### Phase 22: Configuration and Path Resolution
**Goal**: System reads gendoc.json config and resolves all resource paths from network share
**Depends on**: Nothing (first phase of v1.6)
**Requirements**: CFG-01, CFG-02, CFG-03
**Success Criteria** (what must be TRUE):
  1. User can create gendoc.json with network_share_path field and system reads it at startup
  2. If config missing, MCP server returns clear error: "Create gendoc.json with network_share_path"
  3. System validates network share is accessible and contains references/, images/, template at startup
  4. All modules receive paths as parameters (no hardcoded paths except in server.py config loader)
  5. Existing references, images, and template are resolved from the network share path
**Plans**: 2 plans (Wave 1: 22-01, Wave 2: 22-02)

Plans:
- [ ] 22-01-PLAN.md — Config loader with search, load, and validation
- [ ] 22-02-PLAN.md — Refactor server.py to use config-resolved paths

### Phase 23: Output Restructuring
**Goal**: Each devis generation creates isolated output in ./output/{devis_numero}/
**Depends on**: Phase 22
**Requirements**: OUT-01, OUT-02, OUT-03, OUT-04
**Success Criteria** (what must be TRUE):
  1. User generates a devis and finds output in ./output/DEVIS-12345/ (not Delagrave/output/)
  2. PowerPoint file is written to the devis subfolder
  3. LOG.md for the execution is written to the devis subfolder
  4. SP selector HTML and JSON export are written to the devis subfolder
  5. Multiple devis generations create separate folders without conflicts
**Plans**: 3 plans (Wave 1)

Plans:
- [ ] 23-01-PLAN.md — Create devis output directory infrastructure and refactor PipelineLogger
- [ ] 23-02-PLAN.md — Refactor generate_slides for per-devis output paths
- [ ] 23-03-PLAN.md — Refactor SP selector tools for per-devis output paths

### Phase 24: Access Control
**Goal**: Admin flag controls CRUD access, users operate in read-only mode
**Depends on**: Phase 22
**Requirements**: ACL-01, ACL-02, ACL-03
**Success Criteria** (what must be TRUE):
  1. User sets "admin": true in gendoc.json and can execute add_reference, update_reference, delete_reference
  2. User sets "admin": false and CRUD tools return error: "Operation reservee a l'administrateur"
  3. Non-admin users can still analyze devis, generate slides, use SP selector (read-only operations)
  4. Admin validation happens in server.py before delegating to CRUD modules
**Plans**: TBD

### Phase 25: Deployment Package
**Goal**: Complete deployment artifacts for setting up a new workstation
**Depends on**: Phase 22, Phase 23, Phase 24
**Requirements**: DEP-01, DEP-02, DEP-03
**Success Criteria** (what must be TRUE):
  1. User can copy src/gendoc/ package locally and install with pip install -e .
  2. User has a documented MCP config snippet for Claude CLI (claude_desktop_config.json)
  3. User follows a deployment guide to configure a new workstation in <15 minutes
  4. Deployment guide covers: package install, config file creation, MCP registration, test generation
**Plans**: TBD

### Phase 26: Testing and Validation
**Goal**: All existing tests pass, new tests cover config resolution and admin mode
**Depends on**: Phase 22, Phase 23, Phase 24
**Requirements**: REG-01, REG-02, REG-03
**Success Criteria** (what must be TRUE):
  1. All 123 existing tests pass after path refactoring (zero regressions)
  2. New tests validate config loading, path resolution, missing config error
  3. New tests validate admin=true enables CRUD, admin=false blocks CRUD
  4. Test suite runs in <30s (acceptable increase from <20s for new config tests)
**Plans**: TBD

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 22. Configuration and Path Resolution | 0/2 | Complete    | 2026-02-16 |
| 23. Output Restructuring | 0/TBD | Not started | - |
| 24. Access Control | 0/TBD | Not started | - |
| 25. Deployment Package | 0/TBD | Not started | - |
| 26. Testing and Validation | 0/TBD | Not started | - |

## Coverage

**Requirements mapped:** 16/16 (100%)

| Requirement | Phase | Description |
|-------------|-------|-------------|
| CFG-01 | 22 | Read gendoc.json config file |
| CFG-02 | 22 | Error handling for missing config |
| CFG-03 | 22 | Validate network share accessibility |
| OUT-01 | 23 | Create ./output/{devis_numero}/ subdirectory |
| OUT-02 | 23 | Write PowerPoint to devis subfolder |
| OUT-03 | 23 | Write LOG.md to devis subfolder |
| OUT-04 | 23 | Write SP HTML/JSON to devis subfolder |
| ACL-01 | 24 | Admin flag in config |
| ACL-02 | 24 | CRUD tools disabled for non-admins |
| ACL-03 | 24 | Clear error messages for non-admin CRUD |
| DEP-01 | 25 | Package deployable by local copy |
| DEP-02 | 25 | MCP config documented |
| DEP-03 | 25 | Deployment guide created |
| REG-01 | 26 | 123 existing tests pass |
| REG-02 | 26 | Config resolution tests |
| REG-03 | 26 | Admin mode tests |

---
*Roadmap created: 2026-02-16*
