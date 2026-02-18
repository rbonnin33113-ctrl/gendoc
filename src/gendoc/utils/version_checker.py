"""Version checker for gendoc-delagrave.

Reads local version from installed package metadata and compares with the
latest tag on GitHub. Designed to be called at MCP server startup to notify
users of available updates.

Key design constraints:
- No external dependencies (uses urllib.request only)
- Silent failure on any error (network, token, parsing)
- Never crashes or blocks MCP server startup
- No print() calls -- caller decides what to do with the result
"""

import json
import urllib.error
import urllib.request
from importlib.metadata import version as _importlib_version, PackageNotFoundError
from pathlib import Path


def get_local_version() -> str:
    """Read local package version.

    Reads pyproject.toml first (always up to date after git pull), then
    falls back to importlib.metadata (for non-editable installs).

    Returns:
        Version string (e.g., "2.0.0"). Returns "0.0.0" if undetectable.
    """
    # Primary: pyproject.toml (always current after git pull)
    try:
        import re
        current = Path(__file__).resolve()
        for parent in current.parents:
            candidate = parent / "pyproject.toml"
            if candidate.exists():
                content = candidate.read_text(encoding="utf-8")
                match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
                if match:
                    return match.group(1)
                break
    except Exception:
        pass

    # Fallback: importlib.metadata
    try:
        return _importlib_version("gendoc-delagrave")
    except PackageNotFoundError:
        pass

    return "0.0.0"


def _parse_semver(version_str: str) -> tuple[int, int, int]:
    """Parse a semver string into a (major, minor, patch) tuple.

    Args:
        version_str: Version string, optionally prefixed with "v"
                     (e.g., "v2.1.0" or "2.1.0").

    Returns:
        Tuple of (major, minor, patch) integers.

    Raises:
        ValueError: If the string cannot be parsed as semver.
    """
    clean = version_str.strip().lstrip("v")
    parts = clean.split(".")
    if len(parts) < 3:
        raise ValueError(f"Cannot parse semver: '{version_str}'")
    try:
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    except ValueError:
        raise ValueError(f"Non-integer semver component in: '{version_str}'")


def _format_update_message(update_info: dict) -> str:
    """Format a user-facing update notification message in French.

    Args:
        update_info: Dict with needs_update, local_version, remote_version,
                     and optionally release_url.

    Returns:
        Formatted message string if update available, empty string otherwise.
    """
    if not update_info.get("needs_update"):
        return ""

    local = update_info.get("local_version", "?")
    remote = update_info.get("remote_version", "?")
    url = update_info.get("release_url", "")

    msg = f"[gendoc] Mise a jour disponible: v{local} -> v{remote}"
    if url:
        msg += f"\n[gendoc] Voir: {url}"
    return msg


def check_for_update(
    github_repo: str,
    github_token: str | None = None,
) -> dict | None:
    """Compare local version with latest GitHub tag.

    Calls GitHub REST API to retrieve the latest tag for the repository,
    then compares it with the local installed version using semver.

    Args:
        github_repo: Repository in "owner/repo" format (e.g., "RemyBONNIN/gendoc-delagrave").
                     If empty or blank, returns None immediately (silent skip).
        github_token: Optional GitHub personal access token for private repos.
                      If None or empty, the request is made without authentication.

    Returns:
        Dict with keys:
            - needs_update (bool)
            - local_version (str)
            - remote_version (str)
            - release_url (str)  -- only when needs_update is True
        Returns None on any error (network unavailable, invalid token, bad JSON,
        empty tag list, semver parse failure, timeout, etc.).
    """
    try:
        # Skip immediately if no repo configured
        if not github_repo or not github_repo.strip():
            return None

        repo = github_repo.strip()

        # Build request
        url = f"https://api.github.com/repos/{repo}/tags?per_page=1"
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/vnd.github.v3+json")
        req.add_header("User-Agent", "gendoc-delagrave-version-checker")
        if github_token and github_token.strip():
            req.add_header("Authorization", f"token {github_token.strip()}")

        # Execute request with 5-second timeout
        with urllib.request.urlopen(req, timeout=5) as resp:
            raw = resp.read()

        tags = json.loads(raw)

        # No tags published yet
        if not tags:
            return None

        latest_tag = tags[0].get("name", "")
        if not latest_tag:
            return None

        local_ver = get_local_version()
        local_tuple = _parse_semver(local_ver)
        remote_tuple = _parse_semver(latest_tag)
        remote_clean = latest_tag.lstrip("v")

        if remote_tuple > local_tuple:
            return {
                "needs_update": True,
                "local_version": local_ver,
                "remote_version": remote_clean,
                "release_url": f"https://github.com/{repo}/releases/latest",
            }
        else:
            return {
                "needs_update": False,
                "local_version": local_ver,
                "remote_version": remote_clean,
            }

    except Exception:
        # Silent failure -- version check must never crash MCP startup
        return None
