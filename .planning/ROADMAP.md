# Roadmap: Generateur de Fiches Techniques Delagrave

## Milestones

- ✅ **v1.0 Systeme MCP** — Phases 1-6 (shipped 2026-02-10)
- ✅ **v1.1 Qualite et Couverture Familles** — Phases 7-8 (shipped 2026-02-10)
- ✅ **v1.2 Outil de Selection SP** — Phases 9-11 (shipped 2026-02-11)
- 🚧 **v1.3 Robustesse et Logging** — Phases 12-15 (in progress)

## Phases

<details>
<summary>✅ v1.0 Systeme MCP (Phases 1-6) — SHIPPED 2026-02-10</summary>

- [x] Phase 1: Fondation Donnees (2/2 plans) — completed 2026-02-09
- [x] Phase 2: Infrastructure MCP (2/2 plans) — completed 2026-02-10
- [x] Phase 3: Analyse de Devis (2/2 plans) — completed 2026-02-10
- [x] Phase 4: Generation PowerPoint (2/2 plans) — completed 2026-02-10
- [x] Phase 5: Assemblage Document (1/1 plan) — completed 2026-02-10
- [x] Phase 6: Integration Pipeline (1/1 plan) — completed 2026-02-10

</details>

<details>
<summary>✅ v1.1 Qualite et Couverture Familles (Phases 7-8) — SHIPPED 2026-02-10</summary>

- [x] Phase 7: Verification et Correction des Familles (3/3 plans) — completed 2026-02-10
- [x] Phase 8: Suite de Tests Automatises (2/2 plans) — completed 2026-02-10

</details>

<details>
<summary>✅ v1.2 Outil de Selection SP (Phases 9-11) — SHIPPED 2026-02-11</summary>

- [x] Phase 9: Detection et Extraction SP (1/1 plan) — completed 2026-02-10
- [x] Phase 10: Interface HTML Interactive (1/1 plan) — completed 2026-02-11
- [x] Phase 11: Integration MCP File-Based (1/1 plan) — completed 2026-02-11

</details>

### 🚧 v1.3 Robustesse et Logging (In Progress)

**Milestone Goal:** Rendre le pipeline fiable et transparent avec hot-reload MCP, logging complet, detection devis amelioree, et gestion d'erreurs claire.

#### Phase 12: Hot-Reload MCP

**Goal:** Le serveur MCP prend en compte les modifications des modules generateurs sans redemarrage manuel.

**Depends on:** Nothing (independent infrastructure improvement)

**Requirements:** RELOAD-01, RELOAD-02

**Success Criteria** (what must be TRUE):
1. Developer can modify generator modules (modern_template.py, document_assembler.py, pptx_generator.py) and changes are reflected in next MCP tool call without server restart
2. Hot-reload works transparently — no errors if modules haven't changed, no performance degradation
3. Server logs when modules are reloaded with module names and timestamps

**Plans:** TBD

Plans:
- [ ] 12-01: TBD

---

#### Phase 13: Logging Infrastructure

**Goal:** Every pipeline execution creates a structured diagnostic log file that captures all steps, errors, and solutions.

**Depends on:** Nothing (independent infrastructure)

**Requirements:** LOG-01, LOG-02, LOG-03, LOG-04, LOG-05, LOG-06

**Success Criteria** (what must be TRUE):
1. Each /gendoc-full execution creates a timestamped log file in Delagrave/output/logs/
2. Log file contains all pipeline steps (analyze PDF, preview, SP, generation) with durations and outcomes
3. Errors are logged with full context (product code, file path, traceback) and any automatic recovery solutions applied
4. Log file is structured as Markdown with sections: Execution Summary, Input Parameters, Pipeline Steps, Errors Encountered, Solutions Applied
5. Log is AI-readable — an LLM can parse the log and understand what happened, what failed, and how it was resolved

**Plans:** TBD

Plans:
- [ ] 13-01: TBD

---

#### Phase 14: Detection Robustesse

**Goal:** Devis PDF analysis filters out common false positives and logs unknown codes for review.

**Depends on:** Phase 13 (logging system for unknown codes)

**Requirements:** DETECT-01, DETECT-02, DETECT-03

**Success Criteria** (what must be TRUE):
1. Common false positives (850MM, CONDITIONS, LIVRAISON, SALLE, etc.) are filtered during devis analysis
2. Exclusion list is configurable in a dedicated file (e.g., Delagrave/config/exclusions.txt or embedded in code with clear documentation)
3. Unknown product codes (not in catalog, not in exclusions) are logged in the execution log file for later review
4. Preview output clearly separates valid products, SP articles, and unknown codes with counts

**Plans:** TBD

Plans:
- [ ] 14-01: TBD

---

#### Phase 15: Gestion Erreurs et Resume

**Goal:** Pipeline handles errors gracefully and provides compact progress output instead of technical scrolling.

**Depends on:** Phase 13 (logging system to capture errors)

**Requirements:** ERR-01, ERR-02, ERR-03, OUTPUT-01, OUTPUT-02

**Success Criteria** (what must be TRUE):
1. /gendoc-full displays compact progress messages per step (Analyze OK, 28 refs... Generation OK, 45 pages) instead of technical details scrolling
2. Technical details (file paths, debug info) go to log file, not console
3. Generation errors (image missing, template issue, etc.) produce clear user-facing messages with the product code affected
4. Pipeline continues after individual product errors (skip + log) rather than halting completely
5. Final output includes summary of products processed successfully vs. in error with reasons

**Plans:** TBD

Plans:
- [ ] 15-01: TBD

---

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Fondation Donnees | v1.0 | 2/2 | Complete | 2026-02-09 |
| 2. Infrastructure MCP | v1.0 | 2/2 | Complete | 2026-02-10 |
| 3. Analyse de Devis | v1.0 | 2/2 | Complete | 2026-02-10 |
| 4. Generation PowerPoint | v1.0 | 2/2 | Complete | 2026-02-10 |
| 5. Assemblage Document | v1.0 | 1/1 | Complete | 2026-02-10 |
| 6. Integration Pipeline | v1.0 | 1/1 | Complete | 2026-02-10 |
| 7. Verification et Correction des Familles | v1.1 | 3/3 | Complete | 2026-02-10 |
| 8. Suite de Tests Automatises | v1.1 | 2/2 | Complete | 2026-02-10 |
| 9. Detection et Extraction SP | v1.2 | 1/1 | Complete | 2026-02-10 |
| 10. Interface HTML Interactive | v1.2 | 1/1 | Complete | 2026-02-11 |
| 11. Integration MCP File-Based | v1.2 | 1/1 | Complete | 2026-02-11 |
| 12. Hot-Reload MCP | v1.3 | 0/TBD | Not started | - |
| 13. Logging Infrastructure | v1.3 | 0/TBD | Not started | - |
| 14. Detection Robustesse | v1.3 | 0/TBD | Not started | - |
| 15. Gestion Erreurs et Resume | v1.3 | 0/TBD | Not started | - |
