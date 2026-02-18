"""Auto-updater for gendoc-delagrave.

Handles the full update lifecycle: Git detection, installation if absent,
clone or pull from a private GitHub repository, and pip install -e . to
finalize the update.

Key design constraints:
- No external dependencies beyond stdlib + subprocess
- All errors are captured and returned in the result dict -- no unhandled exceptions
- No print() calls -- caller decides what to do with the result
- subprocess.run with capture_output=True and timeout on every call
- All bytes decoded with errors="replace" to avoid UnicodeDecodeError on Windows
"""

import os
import re
import subprocess
import sys
from pathlib import Path

from gendoc.utils.version_checker import get_local_version


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _is_git_installed() -> bool:
    """Check whether git is available on the system PATH.

    Returns:
        True if ``git --version`` exits with code 0, False otherwise
        (including FileNotFoundError when git is not found at all).
    """
    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            timeout=10,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False
    except Exception:
        return False


def _install_git() -> dict:
    """Attempt to install Git via winget on Windows.

    Note: After a winget installation, the current process PATH does NOT yet
    contain the newly installed Git binary. Subsequent git calls must use the
    full path ``C:\\Program Files\\Git\\cmd\\git.exe`` rather than ``"git"``.
    Use ``_get_git_cmd()`` which returns the appropriate command automatically.

    Returns:
        {"ok": True} on success, or {"ok": False, "error": "<message>"} on failure.
    """
    try:
        result = subprocess.run(
            [
                "winget",
                "install",
                "--id",
                "Git.Git",
                "-e",
                "--source",
                "winget",
                "--accept-package-agreements",
                "--accept-source-agreements",
            ],
            capture_output=True,
            timeout=300,
        )
        if result.returncode == 0:
            return {"ok": True}
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        return {"ok": False, "error": stderr or "winget exited with non-zero code"}
    except FileNotFoundError:
        return {"ok": False, "error": "winget non disponible sur ce systeme"}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _get_git_cmd() -> str:
    """Return the git executable to use.

    Tries "git" first (normal PATH lookup). If unavailable, checks the
    well-known winget installation path. Raises RuntimeError if neither works.

    Returns:
        Path/command string suitable for passing as the first element of a
        subprocess argv list.

    Raises:
        RuntimeError: If git is not found anywhere.
    """
    if _is_git_installed():
        return "git"

    # Check the default winget installation path (post-install, PATH not updated)
    fallback = r"C:\Program Files\Git\cmd\git.exe"
    if os.path.isfile(fallback):
        return fallback

    raise RuntimeError(
        "Git introuvable. Installez Git manuellement: https://git-scm.com/download/win"
    )


def _clone_repo(
    git_cmd: str,
    github_repo: str,
    github_token: str | None,
    target_dir: str,
) -> dict:
    """Clone a GitHub repository into target_dir.

    Args:
        git_cmd: Git executable path (from _get_git_cmd).
        github_repo: Repository in "owner/repo" format.
        github_token: Optional PAT for private repos.
        target_dir: Destination directory for the clone.

    Returns:
        {"ok": True} on success, {"ok": False, "error": "<message>"} on failure.
    """
    try:
        if github_token:
            url = f"https://{github_token}@github.com/{github_repo}.git"
        else:
            url = f"https://github.com/{github_repo}.git"

        result = subprocess.run(
            [git_cmd, "clone", url, target_dir],
            capture_output=True,
            timeout=120,
        )
        if result.returncode == 0:
            return {"ok": True}
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        return {"ok": False, "error": stderr or "git clone a echoue"}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _pull_repo(
    git_cmd: str,
    repo_dir: str,
    github_repo: str | None = None,
    github_token: str | None = None,
) -> dict:
    """Run git pull in an existing repository directory.

    If github_token is provided, temporarily sets the remote URL with the
    token embedded so that private repos can authenticate without prompting.

    Args:
        git_cmd: Git executable path (from _get_git_cmd).
        repo_dir: Path to the local repository root.
        github_repo: Repository in "owner/repo" format (optional).
        github_token: GitHub PAT for private repos (optional).

    Returns:
        {"ok": True, "output": "<stdout>"} on success,
        {"ok": False, "error": "<stderr>"} on failure.
    """
    try:
        # Set authenticated remote URL before pulling (for private repos)
        if github_repo and github_token:
            auth_url = f"https://{github_token}@github.com/{github_repo}.git"
            subprocess.run(
                [git_cmd, "remote", "set-url", "origin", auth_url],
                capture_output=True,
                timeout=10,
                cwd=repo_dir,
            )

        result = subprocess.run(
            [git_cmd, "pull"],
            capture_output=True,
            timeout=60,
            cwd=repo_dir,
        )

        # Remove token from remote URL after pull (security)
        if github_repo and github_token:
            clean_url = f"https://github.com/{github_repo}.git"
            subprocess.run(
                [git_cmd, "remote", "set-url", "origin", clean_url],
                capture_output=True,
                timeout=10,
                cwd=repo_dir,
            )

        if result.returncode == 0:
            output = result.stdout.decode("utf-8", errors="replace").strip()
            return {"ok": True, "output": output}
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        return {"ok": False, "error": stderr or "git pull a echoue"}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _pip_install(repo_dir: str) -> dict:
    """Run ``pip install -e .`` in the repository directory.

    Uses ``sys.executable`` to ensure the correct Python interpreter is
    targeted rather than whatever ``pip`` or ``python`` happens to be on PATH.

    Args:
        repo_dir: Path to the local repository root (must contain pyproject.toml).

    Returns:
        {"ok": True} on success, {"ok": False, "error": "<message>"} on failure.
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", "."],
            capture_output=True,
            timeout=120,
            cwd=repo_dir,
        )
        if result.returncode == 0:
            return {"ok": True}
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        return {"ok": False, "error": stderr or "pip install a echoue"}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _read_version_from_pyproject(repo_dir: str) -> str:
    """Read the version string from pyproject.toml in repo_dir.

    Args:
        repo_dir: Path to the repository root.

    Returns:
        Version string (e.g., "2.1.0"). Returns "0.0.0" if file is missing
        or version line cannot be found.
    """
    try:
        pyproject = Path(repo_dir) / "pyproject.toml"
        content = pyproject.read_text(encoding="utf-8")
        match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
        if match:
            return match.group(1)
    except Exception:
        pass
    return "0.0.0"


# ---------------------------------------------------------------------------
# Internal: deduce install directory from current __file__
# ---------------------------------------------------------------------------


def _deduce_install_dir() -> str:
    """Deduce the repository root from this module's location.

    Walks up 4 levels from auto_updater.py:
        auto_updater.py -> utils -> gendoc -> src -> repo_root

    If pyproject.toml is not found at the deduced root, falls back to
    ``C:\\gendoc`` as a conventional installation directory.

    Returns:
        Absolute path string for the repository root.
    """
    try:
        current = Path(__file__).resolve()
        # 4 levels up: utils -> gendoc -> src -> repo_root
        candidate = current.parent.parent.parent.parent
        if (candidate / "pyproject.toml").exists():
            return str(candidate)
    except Exception:
        pass
    return r"C:\gendoc"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def run_update(
    github_repo: str,
    github_token: str | None = None,
    install_dir: str | None = None,
) -> dict:
    """Execute the full auto-update sequence.

    Detects Git, installs it via winget if absent, clones or pulls the
    repository, then runs ``pip install -e .`` to finalise the update.

    Args:
        github_repo: Repository in "owner/repo" format (from gendoc.json).
                     If empty or blank, returns immediately with status "no_repo".
        github_token: Optional GitHub personal access token for private repos.
                      If None, the clone URL will be unauthenticated.
        install_dir: Path to the local repository root. If None, deduced from
                     this file's location (4 levels up). Falls back to
                     ``C:\\gendoc`` if pyproject.toml is not found at the
                     deduced location.

    Returns:
        Dict with keys:
            status (str):           "success" | "error" | "no_repo"
            old_version (str):      Local version before update
            new_version (str):      Version read from pyproject.toml after update
            steps_completed (list): Steps that succeeded before return
            error (str | None):     Error message, or None on success
            needs_restart (bool):   Always True after pip install succeeds
            resume (str):           Human-readable French summary
    """
    # Guard: no repo configured
    if not github_repo or not github_repo.strip():
        return {
            "status": "no_repo",
            "old_version": get_local_version(),
            "new_version": get_local_version(),
            "steps_completed": [],
            "error": "github_repo non configure",
            "needs_restart": False,
            "resume": "Mise a jour impossible: github_repo non configure dans gendoc.json",
        }

    old_version = get_local_version()

    # Resolve installation directory
    if install_dir is None:
        install_dir = _deduce_install_dir()

    steps_completed: list[str] = []

    repo_has_git = (Path(install_dir) / ".git").exists()

    if not repo_has_git:
        # Need to clone -- ensure Git is available first
        if not _is_git_installed():
            install_result = _install_git()
            if not install_result["ok"]:
                return {
                    "status": "error",
                    "old_version": old_version,
                    "new_version": old_version,
                    "steps_completed": steps_completed,
                    "error": install_result.get("error", "Installation Git echouee"),
                    "needs_restart": False,
                    "resume": (
                        "Git non installe et installation automatique echouee. "
                        "Installez Git manuellement: https://git-scm.com/download/win"
                    ),
                }
            steps_completed.append("git_installed")

        try:
            git_cmd = _get_git_cmd()
        except RuntimeError as exc:
            return {
                "status": "error",
                "old_version": old_version,
                "new_version": old_version,
                "steps_completed": steps_completed,
                "error": str(exc),
                "needs_restart": False,
                "resume": (
                    "Git non installe et installation automatique echouee. "
                    "Installez Git manuellement: https://git-scm.com/download/win"
                ),
            }

        clone_result = _clone_repo(git_cmd, github_repo, github_token, install_dir)
        if not clone_result["ok"]:
            return {
                "status": "error",
                "old_version": old_version,
                "new_version": old_version,
                "steps_completed": steps_completed,
                "error": clone_result.get("error", "Clone echoue"),
                "needs_restart": False,
                "resume": (
                    "Echec du clone GitHub. "
                    "Verifiez le token dans gendoc.json et la connexion reseau."
                ),
            }
        steps_completed.append("git_clone")

    else:
        # Pull existing repo
        try:
            git_cmd = _get_git_cmd()
        except RuntimeError as exc:
            return {
                "status": "error",
                "old_version": old_version,
                "new_version": old_version,
                "steps_completed": steps_completed,
                "error": str(exc),
                "needs_restart": False,
                "resume": (
                    "Git non installe et installation automatique echouee. "
                    "Installez Git manuellement: https://git-scm.com/download/win"
                ),
            }

        pull_result = _pull_repo(git_cmd, install_dir, github_repo, github_token)
        if not pull_result["ok"]:
            return {
                "status": "error",
                "old_version": old_version,
                "new_version": old_version,
                "steps_completed": steps_completed,
                "error": pull_result.get("error", "git pull echoue"),
                "needs_restart": False,
                "resume": (
                    "Echec de git pull. "
                    "Conflit possible -- contactez l'administrateur."
                ),
            }
        steps_completed.append("git_pull")

        # Skip pip if git pull said "Already up to date"
        pull_output = pull_result.get("output", "")
        if "Already up to date" in pull_output or "Already up-to-date" in pull_output:
            new_version = _read_version_from_pyproject(install_dir)
            return {
                "status": "success",
                "old_version": old_version,
                "new_version": new_version,
                "steps_completed": steps_completed,
                "error": None,
                "needs_restart": False,
                "resume": f"Deja a jour (v{new_version}). Aucun changement.",
            }

    # Clone path needs pip install (first install).
    # Pull path skips pip — editable install already links source files,
    # and pip can hang on Windows due to file locking when MCP is running.
    if not repo_has_git:
        # Was a clone — need pip install
        pip_result = _pip_install(install_dir)
        if not pip_result["ok"]:
            return {
                "status": "error",
                "old_version": old_version,
                "new_version": old_version,
                "steps_completed": steps_completed,
                "error": pip_result.get("error", "pip install echoue"),
                "needs_restart": False,
                "resume": (
                    f"git clone OK mais pip install echoue. "
                    f"Essayez manuellement: pip install -e {install_dir}"
                ),
            }
        steps_completed.append("pip_install")

    new_version = _read_version_from_pyproject(install_dir)

    if new_version == old_version:
        resume = f"Deja a jour (v{new_version}). Aucun changement."
    else:
        resume = (
            f"Mise a jour OK: v{old_version} -> v{new_version}. "
            "Redemarrez Claude pour appliquer."
        )

    return {
        "status": "success",
        "old_version": old_version,
        "new_version": new_version,
        "steps_completed": steps_completed,
        "error": None,
        "needs_restart": True,
        "resume": resume,
    }
