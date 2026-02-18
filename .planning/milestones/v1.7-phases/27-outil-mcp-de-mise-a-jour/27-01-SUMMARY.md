---
phase: 27-outil-mcp-de-mise-a-jour
plan: 01
subsystem: infra
tags: [auto-update, subprocess, git, pip, winget, version-management]

# Dependency graph
requires:
  - phase: 26-versioning-et-detection
    provides: get_local_version() from version_checker.py
provides:
  - auto_updater.py with run_update() orchestrator
  - _is_git_installed, _install_git, _get_git_cmd helpers
  - _clone_repo, _pull_repo, _pip_install subprocess wrappers
  - _read_version_from_pyproject for post-update version detection
  - 25 unit tests with full subprocess mock coverage
affects:
  - 27-02 (MCP tool update_gendoc will call run_update)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - subprocess.run with capture_output=True and timeout on every call
    - bytes decoded with errors="replace" to avoid UnicodeDecodeError on Windows
    - sys.executable for pip to target the correct Python interpreter
    - All errors captured in dict with French resume field, no unhandled exceptions
    - _get_git_cmd() handles post-winget PATH gap via direct exe path fallback

key-files:
  created:
    - src/gendoc/utils/auto_updater.py
    - tests/test_auto_updater.py
  modified: []

key-decisions:
  - "sys.executable used for pip to target correct interpreter regardless of PATH"
  - "Post-winget PATH gap handled by _get_git_cmd() checking C:\\Program Files\\Git\\cmd\\git.exe"
  - "install_dir deduced 4 levels up from __file__; falls back to C:\\gendoc if pyproject.toml missing"
  - "All errors returned in dict with French resume field -- no exceptions propagate to caller"

patterns-established:
  - "Auto-update helper pattern: each sub-step returns {ok, error} dict for clean error chaining"

# Metrics
duration: 20min
completed: 2026-02-18
---

# Phase 27 Plan 01: Auto-Updater Core Module Summary

**auto_updater.py with run_update() orchestrating Git detection, winget install, clone/pull, and pip install -e . -- 25 mocked unit tests covering all paths including post-winget PATH gap handling**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-02-18T13:24:13Z
- **Completed:** 2026-02-18T13:44:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Created auto_updater.py with run_update() accepting github_repo, github_token, install_dir
- All 7 sub-functions implemented: _is_git_installed, _install_git, _get_git_cmd, _clone_repo, _pull_repo, _pip_install, _read_version_from_pyproject
- 25 unit tests added covering all helpers and all run_update() scenarios including error paths
- Full suite passes: 184 tests, 0 failures (up from 159)

## Task Commits

Each task was committed atomically:

1. **Task 1: Creer le module auto_updater.py** - `c88e0b0` (feat)
2. **Task 2: Tests unitaires auto_updater + verification globale** - `d44e37d` (test)

## Files Created/Modified
- `src/gendoc/utils/auto_updater.py` - Auto-update core module with run_update() and all helpers
- `tests/test_auto_updater.py` - 25 unit tests with full subprocess mock coverage

## Decisions Made
- `sys.executable` used for pip to always target the current Python interpreter (no PATH ambiguity)
- Post-winget PATH gap handled: `_get_git_cmd()` checks `C:\Program Files\Git\cmd\git.exe` as fallback when `git` is not on PATH yet
- `install_dir` deduced by going 4 levels up from `__file__` (auto_updater -> utils -> gendoc -> src -> root); falls back to `C:\gendoc` if `pyproject.toml` not found at deduced root
- Every error path returns a structured dict with a French `resume` field -- no exceptions escape `run_update()`

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- auto_updater.py is ready to be called by the MCP tool update_gendoc (Plan 02)
- The module exports run_update() with the exact signature Plan 02 will use
- 184 tests passing, zero regressions

## Self-Check: PASSED
- `src/gendoc/utils/auto_updater.py` - FOUND
- `tests/test_auto_updater.py` - FOUND
- commit `c88e0b0` - FOUND
- commit `d44e37d` - FOUND

---
*Phase: 27-outil-mcp-de-mise-a-jour*
*Completed: 2026-02-18*
