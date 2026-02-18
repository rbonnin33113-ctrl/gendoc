"""Tests for gendoc.utils.version_checker module.

Covers local version reading, semver parsing, GitHub API comparison,
and update message formatting. All network calls are mocked.
"""

import json
import pytest
import urllib.error
from unittest.mock import patch, MagicMock

from gendoc.utils.version_checker import (
    get_local_version,
    check_for_update,
    _parse_semver,
    _format_update_message,
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _mock_github_response(tag_name: str):
    """Return a mock urllib response that looks like a GitHub tags API reply."""
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps([{"name": tag_name}]).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


# ---------------------------------------------------------------------------
# get_local_version
# ---------------------------------------------------------------------------

def test_get_local_version():
    """Version should match pyproject.toml which is pinned to 2.0.0."""
    version = get_local_version()
    assert version == "2.0.0", f"Expected '2.0.0', got '{version}'"


def test_get_local_version_returns_string():
    """get_local_version always returns a non-empty string."""
    version = get_local_version()
    assert isinstance(version, str)
    assert len(version) > 0


# ---------------------------------------------------------------------------
# _parse_semver
# ---------------------------------------------------------------------------

def test_parse_semver_with_v_prefix():
    """_parse_semver strips the leading 'v' before parsing."""
    assert _parse_semver("v2.1.0") == (2, 1, 0)


def test_parse_semver_without_prefix():
    """_parse_semver handles bare X.Y.Z format."""
    assert _parse_semver("1.0.0") == (1, 0, 0)


def test_parse_semver_zero_version():
    """_parse_semver handles 0.0.0."""
    assert _parse_semver("0.0.0") == (0, 0, 0)


def test_parse_semver_large_numbers():
    """_parse_semver handles large version numbers."""
    assert _parse_semver("10.20.300") == (10, 20, 300)


def test_parse_semver_invalid():
    """_parse_semver raises ValueError for non-numeric strings."""
    with pytest.raises(ValueError):
        _parse_semver("abc")


def test_parse_semver_invalid_partial():
    """_parse_semver raises ValueError for strings with fewer than 3 parts."""
    with pytest.raises(ValueError):
        _parse_semver("1.0")


# ---------------------------------------------------------------------------
# check_for_update -- no repo configured
# ---------------------------------------------------------------------------

def test_check_for_update_no_repo():
    """check_for_update returns None immediately when repo is empty."""
    result = check_for_update("", None)
    assert result is None


def test_check_for_update_whitespace_repo():
    """check_for_update returns None when repo is only whitespace."""
    result = check_for_update("   ", None)
    assert result is None


# ---------------------------------------------------------------------------
# check_for_update -- network errors
# ---------------------------------------------------------------------------

def test_check_for_update_network_error():
    """check_for_update returns None on URLError without raising."""
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("offline")):
        result = check_for_update("owner/repo", None)
    assert result is None


def test_check_for_update_timeout():
    """check_for_update returns None on TimeoutError without raising."""
    with patch("urllib.request.urlopen", side_effect=TimeoutError("timed out")):
        result = check_for_update("owner/repo", None)
    assert result is None


def test_check_for_update_generic_exception():
    """check_for_update returns None on any unexpected exception."""
    with patch("urllib.request.urlopen", side_effect=RuntimeError("unexpected")):
        result = check_for_update("owner/repo", None)
    assert result is None


# ---------------------------------------------------------------------------
# check_for_update -- version comparison scenarios
# ---------------------------------------------------------------------------

def test_check_for_update_newer_version():
    """When remote tag is newer, needs_update is True with correct fields."""
    with patch("urllib.request.urlopen", return_value=_mock_github_response("v3.0.0")):
        result = check_for_update("owner/repo", None)

    assert result is not None
    assert result["needs_update"] is True
    assert result["remote_version"] == "3.0.0"
    assert "local_version" in result
    assert "release_url" in result
    assert "owner/repo" in result["release_url"]


def test_check_for_update_same_version():
    """When remote tag matches local version, needs_update is False."""
    with patch("urllib.request.urlopen", return_value=_mock_github_response("v2.0.0")):
        result = check_for_update("owner/repo", None)

    assert result is not None
    assert result["needs_update"] is False
    assert result["remote_version"] == "2.0.0"


def test_check_for_update_older_remote():
    """When remote tag is older than local, needs_update is False."""
    with patch("urllib.request.urlopen", return_value=_mock_github_response("v1.0.0")):
        result = check_for_update("owner/repo", None)

    assert result is not None
    assert result["needs_update"] is False


def test_check_for_update_empty_tags():
    """When GitHub returns an empty tag list, returns None."""
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps([]).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = check_for_update("owner/repo", None)

    assert result is None


def test_check_for_update_with_token():
    """Token is accepted without error (request still goes through mock)."""
    with patch("urllib.request.urlopen", return_value=_mock_github_response("v2.0.0")):
        result = check_for_update("owner/repo", "ghp_fake_token")

    assert result is not None
    assert result["needs_update"] is False


# ---------------------------------------------------------------------------
# _format_update_message
# ---------------------------------------------------------------------------

def test_format_update_message_with_update():
    """Update message contains local/remote version and release URL."""
    info = {
        "needs_update": True,
        "local_version": "2.0.0",
        "remote_version": "3.0.0",
        "release_url": "https://github.com/owner/repo/releases/latest",
    }
    msg = _format_update_message(info)

    assert "2.0.0" in msg
    assert "3.0.0" in msg
    assert "https://github.com/owner/repo/releases/latest" in msg
    assert "[gendoc]" in msg


def test_format_update_message_no_update():
    """When needs_update is False, message is empty string."""
    info = {
        "needs_update": False,
        "local_version": "2.0.0",
        "remote_version": "2.0.0",
    }
    msg = _format_update_message(info)
    assert msg == ""


def test_format_update_message_empty_dict():
    """Empty dict returns empty string (no crash)."""
    msg = _format_update_message({})
    assert msg == ""
