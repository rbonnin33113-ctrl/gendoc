"""Tests for gendoc.utils.auto_updater module.

Covers all helper functions and the run_update() orchestrator.
All subprocess, os.path, and Path calls are mocked -- no real git,
pip, or winget processes are executed.
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, call

from gendoc.utils.auto_updater import (
    run_update,
    _is_git_installed,
    _install_git,
    _get_git_cmd,
    _clone_repo,
    _pull_repo,
    _pip_install,
    _read_version_from_pyproject,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_proc(returncode: int, stdout: bytes = b"", stderr: bytes = b"") -> MagicMock:
    """Create a mock subprocess.CompletedProcess-like object."""
    m = MagicMock()
    m.returncode = returncode
    m.stdout = stdout
    m.stderr = stderr
    return m


# ---------------------------------------------------------------------------
# Group 1 -- _is_git_installed
# ---------------------------------------------------------------------------


def test_is_git_installed_true():
    """Returns True when git --version exits with code 0."""
    with patch("gendoc.utils.auto_updater.subprocess.run", return_value=_make_proc(0)):
        assert _is_git_installed() is True


def test_is_git_installed_false():
    """Returns False when git --version exits with non-zero code."""
    with patch("gendoc.utils.auto_updater.subprocess.run", return_value=_make_proc(1)):
        assert _is_git_installed() is False


def test_is_git_installed_not_found():
    """Returns False when git binary is not found (FileNotFoundError)."""
    with patch(
        "gendoc.utils.auto_updater.subprocess.run", side_effect=FileNotFoundError
    ):
        assert _is_git_installed() is False


# ---------------------------------------------------------------------------
# Group 2 -- _install_git
# ---------------------------------------------------------------------------


def test_install_git_success():
    """Returns {"ok": True} when winget exits with code 0."""
    with patch("gendoc.utils.auto_updater.subprocess.run", return_value=_make_proc(0)):
        result = _install_git()
    assert result == {"ok": True}


def test_install_git_failure():
    """Returns {"ok": False, "error": ...} when winget exits with non-zero code."""
    with patch(
        "gendoc.utils.auto_updater.subprocess.run",
        return_value=_make_proc(1, stderr=b"winget: download failed"),
    ):
        result = _install_git()
    assert result["ok"] is False
    assert "error" in result
    assert "winget: download failed" in result["error"]


# ---------------------------------------------------------------------------
# Group 3 -- _clone_repo / _pull_repo
# ---------------------------------------------------------------------------


def test_clone_repo_success():
    """Returns {"ok": True} when git clone exits with code 0."""
    with patch("gendoc.utils.auto_updater.subprocess.run", return_value=_make_proc(0)):
        result = _clone_repo("git", "owner/repo", None, r"C:\gendoc")
    assert result == {"ok": True}


def test_clone_repo_with_token():
    """Verifies that the clone URL contains the token when provided."""
    captured_args = []

    def fake_run(args, **kwargs):
        captured_args.extend(args)
        return _make_proc(0)

    with patch("gendoc.utils.auto_updater.subprocess.run", side_effect=fake_run):
        _clone_repo("git", "owner/repo", "ghp_mytoken", r"C:\gendoc")

    # The URL argument should contain the token
    url_arg = next((a for a in captured_args if "github.com" in a), None)
    assert url_arg is not None
    assert "ghp_mytoken" in url_arg
    assert "owner/repo" in url_arg


def test_clone_repo_failure():
    """Returns {"ok": False, "error": ...} when git clone exits with code 128."""
    with patch(
        "gendoc.utils.auto_updater.subprocess.run",
        return_value=_make_proc(128, stderr=b"Repository not found"),
    ):
        result = _clone_repo("git", "owner/repo", None, r"C:\gendoc")
    assert result["ok"] is False
    assert "Repository not found" in result["error"]


def test_pull_repo_success():
    """Returns {"ok": True, "output": ...} when git pull exits with code 0."""
    with patch(
        "gendoc.utils.auto_updater.subprocess.run",
        return_value=_make_proc(0, stdout=b"Already up to date."),
    ):
        result = _pull_repo("git", r"C:\gendoc")
    assert result["ok"] is True
    assert "output" in result
    assert "Already up to date" in result["output"]


def test_pull_repo_failure():
    """Returns {"ok": False, "error": ...} when git pull exits with non-zero."""
    with patch(
        "gendoc.utils.auto_updater.subprocess.run",
        return_value=_make_proc(1, stderr=b"CONFLICT: merge conflict in foo.py"),
    ):
        result = _pull_repo("git", r"C:\gendoc")
    assert result["ok"] is False
    assert "CONFLICT" in result["error"]


# ---------------------------------------------------------------------------
# Group 4 -- _pip_install
# ---------------------------------------------------------------------------


def test_pip_install_success():
    """Returns {"ok": True} when pip install -e . exits with code 0."""
    with patch("gendoc.utils.auto_updater.subprocess.run", return_value=_make_proc(0)):
        result = _pip_install(r"C:\gendoc")
    assert result == {"ok": True}


def test_pip_install_failure():
    """Returns {"ok": False, "error": ...} when pip exits with non-zero."""
    with patch(
        "gendoc.utils.auto_updater.subprocess.run",
        return_value=_make_proc(1, stderr=b"No module named pip"),
    ):
        result = _pip_install(r"C:\gendoc")
    assert result["ok"] is False
    assert "No module named pip" in result["error"]


# ---------------------------------------------------------------------------
# Group 5 -- _read_version_from_pyproject
# ---------------------------------------------------------------------------


def test_read_version_from_pyproject_success(tmp_path):
    """Extracts version string from a valid pyproject.toml."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[tool.poetry]\nname = "gendoc"\nversion = "1.2.3"\n', encoding="utf-8"
    )
    result = _read_version_from_pyproject(str(tmp_path))
    assert result == "1.2.3"


def test_read_version_from_pyproject_missing(tmp_path):
    """Returns '0.0.0' when pyproject.toml does not exist."""
    result = _read_version_from_pyproject(str(tmp_path))
    assert result == "0.0.0"


# ---------------------------------------------------------------------------
# Group 6 -- run_update (integration mocked)
# ---------------------------------------------------------------------------


def test_run_update_no_repo():
    """Returns {"status": "no_repo"} immediately when github_repo is empty."""
    result = run_update("")
    assert result["status"] == "no_repo"
    assert result["steps_completed"] == []
    assert result["needs_restart"] is False
    assert "resume" in result
    assert result["resume"]


def test_run_update_pull_success(tmp_path):
    """Pull path: .git exists -> git pull OK + pip OK -> status success."""
    # Create .git dir to simulate existing repo
    (tmp_path / ".git").mkdir()
    # Write a fake pyproject.toml so new_version can be read
    (tmp_path / "pyproject.toml").write_text(
        'version = "2.1.0"\n', encoding="utf-8"
    )

    with (
        patch("gendoc.utils.auto_updater.get_local_version", return_value="2.0.0"),
        patch("gendoc.utils.auto_updater._is_git_installed", return_value=True),
        patch(
            "gendoc.utils.auto_updater.subprocess.run", return_value=_make_proc(0)
        ),
    ):
        result = run_update("owner/repo", install_dir=str(tmp_path))

    assert result["status"] == "success"
    assert "git_pull" in result["steps_completed"]
    assert "pip_install" in result["steps_completed"]
    assert result["old_version"] == "2.0.0"
    assert result["new_version"] == "2.1.0"
    assert result["needs_restart"] is True


def test_run_update_clone_success(tmp_path):
    """Clone path: no .git + git installed + clone OK + pip OK -> status success."""
    # No .git dir -- forces clone path
    (tmp_path / "pyproject.toml").write_text(
        'version = "2.1.0"\n', encoding="utf-8"
    )

    with (
        patch("gendoc.utils.auto_updater.get_local_version", return_value="2.0.0"),
        patch("gendoc.utils.auto_updater._is_git_installed", return_value=True),
        patch(
            "gendoc.utils.auto_updater.subprocess.run", return_value=_make_proc(0)
        ),
    ):
        result = run_update("owner/repo", install_dir=str(tmp_path))

    assert result["status"] == "success"
    assert "git_clone" in result["steps_completed"]
    assert "pip_install" in result["steps_completed"]
    assert "git_pull" not in result["steps_completed"]


def test_run_update_git_install_then_clone(tmp_path):
    """Git not installed -> winget OK -> clone OK -> pip OK -> success."""
    (tmp_path / "pyproject.toml").write_text(
        'version = "2.1.0"\n', encoding="utf-8"
    )

    # Fake git exe exists after winget install
    fake_git = tmp_path / "git.exe"
    fake_git.write_bytes(b"")

    with (
        patch("gendoc.utils.auto_updater.get_local_version", return_value="2.0.0"),
        # _is_git_installed returns False (git not on PATH)
        patch("gendoc.utils.auto_updater._is_git_installed", return_value=False),
        # _install_git succeeds
        patch(
            "gendoc.utils.auto_updater._install_git", return_value={"ok": True}
        ),
        # _get_git_cmd returns "git" (mocked -- pretend it works after install)
        patch("gendoc.utils.auto_updater._get_git_cmd", return_value="git"),
        # All subprocess.run calls succeed
        patch(
            "gendoc.utils.auto_updater.subprocess.run", return_value=_make_proc(0)
        ),
    ):
        result = run_update("owner/repo", install_dir=str(tmp_path))

    assert result["status"] == "success"
    assert "git_installed" in result["steps_completed"]
    assert "git_clone" in result["steps_completed"]
    assert "pip_install" in result["steps_completed"]


def test_run_update_pip_failure(tmp_path):
    """git pull OK with changes but pip install fails -> status error."""
    (tmp_path / ".git").mkdir()

    with (
        patch("gendoc.utils.auto_updater.get_local_version", return_value="2.0.0"),
        patch("gendoc.utils.auto_updater._is_git_installed", return_value=True),
        patch(
            "gendoc.utils.auto_updater.subprocess.run",
            side_effect=[
                _make_proc(0, stdout=b"Updating a3ca219..88d4ad5"),  # git pull with changes
                _make_proc(1, stderr=b"pip install failed"),          # pip install
            ],
        ),
    ):
        result = run_update("owner/repo", install_dir=str(tmp_path))

    assert result["status"] == "error"
    assert "git_pull" in result["steps_completed"]
    assert "pip_install" not in result["steps_completed"]
    assert result["needs_restart"] is False


def test_run_update_already_up_to_date_skips_pip(tmp_path):
    """git pull says 'Already up to date' -> skip pip, return success immediately."""
    (tmp_path / ".git").mkdir()
    (tmp_path / "pyproject.toml").write_text('version = "2.0.0"')

    with (
        patch("gendoc.utils.auto_updater.get_local_version", return_value="2.0.0"),
        patch("gendoc.utils.auto_updater._is_git_installed", return_value=True),
        patch(
            "gendoc.utils.auto_updater.subprocess.run",
            side_effect=[
                _make_proc(0, stdout=b"Already up to date."),  # git pull
            ],
        ),
    ):
        result = run_update("owner/repo", install_dir=str(tmp_path))

    assert result["status"] == "success"
    assert "git_pull" in result["steps_completed"]
    assert "pip_install" not in result["steps_completed"]
    assert result["needs_restart"] is False
    assert "Deja a jour" in result["resume"]


def test_run_update_returns_resume(tmp_path):
    """The 'resume' field is always present and non-empty in every outcome."""
    # Test with no_repo
    r1 = run_update("")
    assert "resume" in r1 and r1["resume"]

    # Test with success (pull path)
    (tmp_path / ".git").mkdir()
    (tmp_path / "pyproject.toml").write_text('version = "2.0.0"\n', encoding="utf-8")

    with (
        patch("gendoc.utils.auto_updater.get_local_version", return_value="2.0.0"),
        patch("gendoc.utils.auto_updater._is_git_installed", return_value=True),
        patch(
            "gendoc.utils.auto_updater.subprocess.run", return_value=_make_proc(0)
        ),
    ):
        r2 = run_update("owner/repo", install_dir=str(tmp_path))

    assert "resume" in r2 and r2["resume"]

    # Test with error (pull failure)
    with (
        patch("gendoc.utils.auto_updater.get_local_version", return_value="2.0.0"),
        patch("gendoc.utils.auto_updater._is_git_installed", return_value=True),
        patch(
            "gendoc.utils.auto_updater.subprocess.run",
            return_value=_make_proc(1, stderr=b"error"),
        ),
    ):
        r3 = run_update("owner/repo", install_dir=str(tmp_path))

    assert "resume" in r3 and r3["resume"]


def test_run_update_whitespace_repo():
    """Returns no_repo when github_repo is only whitespace."""
    result = run_update("   ")
    assert result["status"] == "no_repo"


def test_run_update_clone_git_not_installed_winget_fails(tmp_path):
    """No git + winget fails -> error with helpful message."""
    with (
        patch("gendoc.utils.auto_updater.get_local_version", return_value="2.0.0"),
        patch("gendoc.utils.auto_updater._is_git_installed", return_value=False),
        patch(
            "gendoc.utils.auto_updater._install_git",
            return_value={"ok": False, "error": "winget offline"},
        ),
    ):
        result = run_update("owner/repo", install_dir=str(tmp_path))

    assert result["status"] == "error"
    assert "git-scm.com" in result["resume"]
    assert "git_installed" not in result["steps_completed"]


def test_run_update_clone_failure(tmp_path):
    """Clone fails -> error with network/token hint in resume."""
    with (
        patch("gendoc.utils.auto_updater.get_local_version", return_value="2.0.0"),
        patch("gendoc.utils.auto_updater._is_git_installed", return_value=True),
        patch(
            "gendoc.utils.auto_updater.subprocess.run",
            return_value=_make_proc(128, stderr=b"auth failed"),
        ),
    ):
        result = run_update("owner/repo", install_dir=str(tmp_path))

    assert result["status"] == "error"
    assert "token" in result["resume"].lower() or "clone" in result["resume"].lower()


def test_run_update_same_version_resume(tmp_path):
    """When version doesn't change, resume says 'Deja a jour'."""
    (tmp_path / ".git").mkdir()
    (tmp_path / "pyproject.toml").write_text('version = "2.0.0"\n', encoding="utf-8")

    with (
        patch("gendoc.utils.auto_updater.get_local_version", return_value="2.0.0"),
        patch("gendoc.utils.auto_updater._is_git_installed", return_value=True),
        patch(
            "gendoc.utils.auto_updater.subprocess.run", return_value=_make_proc(0)
        ),
    ):
        result = run_update("owner/repo", install_dir=str(tmp_path))

    assert result["status"] == "success"
    assert "Deja a jour" in result["resume"]


def test_run_update_version_upgrade_resume(tmp_path):
    """When version changes, resume contains old -> new version info."""
    (tmp_path / ".git").mkdir()
    (tmp_path / "pyproject.toml").write_text('version = "2.1.0"\n', encoding="utf-8")

    with (
        patch("gendoc.utils.auto_updater.get_local_version", return_value="2.0.0"),
        patch("gendoc.utils.auto_updater._is_git_installed", return_value=True),
        patch(
            "gendoc.utils.auto_updater.subprocess.run", return_value=_make_proc(0)
        ),
    ):
        result = run_update("owner/repo", install_dir=str(tmp_path))

    assert "2.0.0" in result["resume"]
    assert "2.1.0" in result["resume"]
    assert "Redemarrez" in result["resume"]
