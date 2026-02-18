---
phase: 26-versioning-et-detection
plan: 01
subsystem: infra
tags: [versioning, semver, github-api, urllib, importlib-metadata, mcp]

# Dependency graph
requires: []
provides:
  - "version_checker.py module with get_local_version() and check_for_update() using urllib (no extra deps)"
  - "Silent GitHub API version comparison at MCP server startup"
  - "French update notification message on stderr when newer version available"
  - "github_repo and github_token optional fields in config_loader / gendoc.json"
  - "__init__.__version__ synced dynamically from pyproject.toml via importlib.metadata"
affects:
  - "27-auto-update (will build on check_for_update() result)"
  - "server.py startup sequence"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Silent-failure pattern: version check wrapped in try/except, returns None on any error"
    - "urllib.request for HTTP (no extra deps): used instead of requests for lightweight GitHub API calls"
    - "importlib.metadata for installed version reading, pyproject.toml regex as fallback"

key-files:
  created:
    - src/gendoc/utils/version_checker.py
    - tests/test_version_checker.py
  modified:
    - src/gendoc/__init__.py
    - src/gendoc/utils/config_loader.py
    - src/gendoc/mcp/server.py
    - tests/test_config_loader.py

key-decisions:
  - "urllib.request used instead of requests to avoid adding a new dependency"
  - "Silent failure (return None) on any error -- version check must never block MCP startup"
  - "GitHub tags API (/repos/{owner}/{repo}/tags?per_page=1) used instead of /releases to match tag-based versioning"
  - "github_repo and github_token are optional in gendoc.json -- no check performed if absent"

patterns-established:
  - "check_for_update() returns None on failure, dict with needs_update on success -- caller decides output"
  - "Version check block in server.py uses try/except at outermost level for guaranteed non-blocking"

# Metrics
duration: 4min
completed: 2026-02-18
---

# Phase 26 Plan 01: Versioning et Detection Summary

**Version checker module using urllib + importlib.metadata compares local semver against latest GitHub tag at MCP startup, printing French notification to stderr only when update available**

## Performance

- **Duration:** ~4 min
- **Started:** 2026-02-18T11:37:38Z
- **Completed:** 2026-02-18T11:40:54Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments
- Created `version_checker.py` with `get_local_version()`, `check_for_update()`, `_parse_semver()`, `_format_update_message()` using only stdlib
- Integrated non-blocking version check at MCP server startup (silent if github_repo absent or any error)
- Added `github_repo` and `github_token` optional fields to `config_loader.py` and `ConfigDict`
- Synchronized `__init__.__version__` with pyproject.toml dynamically via importlib.metadata
- Created 21 unit tests (all pass) covering semver parsing, network mocking, version comparison scenarios, message formatting

## Task Commits

Each task was committed atomically:

1. **Task 1: Creer le module version_checker.py** - `aaf7689` (feat)
2. **Task 2: Integrer au demarrage MCP + config + tests** - `d84b761` (feat)

**Plan metadata:** (see final commit below)

## Files Created/Modified
- `src/gendoc/utils/version_checker.py` - Core module: local version reading, GitHub API call, semver comparison, message formatting
- `tests/test_version_checker.py` - 21 unit tests covering all functions with urllib mocks
- `src/gendoc/__init__.py` - `__version__` now reads from importlib.metadata instead of hardcoded "0.1.0"
- `src/gendoc/utils/config_loader.py` - Added `github_repo` and `github_token` optional fields to ConfigDict and load_config()
- `src/gendoc/mcp/server.py` - Version check block inserted after config load, before FastMCP instance
- `tests/test_config_loader.py` - Updated key assertion to include new github_repo/github_token fields

## Decisions Made
- **urllib.request vs requests:** Used urllib (stdlib) to avoid adding a dependency for a non-critical feature.
- **GitHub tags API:** Used `/tags?per_page=1` endpoint — simpler than `/releases/latest` and consistent with tag-based versioning.
- **Silent failure design:** `check_for_update()` catches all exceptions and returns `None`. MCP startup is never blocked.
- **Optional GitHub config:** If `github_repo` absent from `gendoc.json`, check is skipped entirely — zero friction for users who don't configure it.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Updated test_config_loader assertion to include new keys**
- **Found during:** Task 2 (full test suite run)
- **Issue:** `test_load_config_from_cwd` checked `set(result.keys()) == {6 original keys}` — adding `github_repo` and `github_token` to the return dict caused this assertion to fail
- **Fix:** Updated the set in the assertion to include `"github_repo"` and `"github_token"` (8 keys total)
- **Files modified:** `tests/test_config_loader.py`
- **Verification:** All 159 tests pass after fix
- **Committed in:** `d84b761` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - test assertion updated to match new contract)
**Impact on plan:** Necessary correctness fix. No scope creep.

## Issues Encountered
None.

## User Setup Required
To enable version checking, add to `gendoc.json`:
```json
{
    "network_share_path": "...",
    "admin": false,
    "github_repo": "RemyBONNIN/gendoc-delagrave",
    "github_token": "ghp_your_token_here"
}
```
If these fields are absent, the version check is silently skipped.

## Next Phase Readiness
- `check_for_update()` and `_format_update_message()` ready for use by Phase 27 (auto-update execution)
- Config fields `github_repo` / `github_token` already wired through config_loader and available in server.py
- All 159 tests passing, no regressions

---
*Phase: 26-versioning-et-detection*
*Completed: 2026-02-18*

## Self-Check: PASSED

All claimed files confirmed present on disk. All claimed commits confirmed in git log.

| Item | Status |
|------|--------|
| src/gendoc/utils/version_checker.py | FOUND |
| tests/test_version_checker.py | FOUND |
| src/gendoc/__init__.py | FOUND |
| src/gendoc/utils/config_loader.py | FOUND |
| src/gendoc/mcp/server.py | FOUND |
| tests/test_config_loader.py | FOUND |
| .planning/phases/26-versioning-et-detection/26-01-SUMMARY.md | FOUND |
| Commit aaf7689 | FOUND |
| Commit d84b761 | FOUND |
