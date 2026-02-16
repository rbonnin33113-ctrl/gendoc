"""
Pytest configuration and shared fixtures for gendoc tests.

This module provides session-scoped fixtures that all tests can use:
- project_root: Path to the repository root
- references_dir: Path to Delagrave/references/
- template_path: Path to the PowerPoint template .potm file
- output_dir: Path to tests/output/ for test-generated files
- sample_codes: Dict mapping family names to known valid product codes
"""

import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def project_root():
    """Return the repository root directory."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def references_dir(project_root):
    """Return path to Delagrave/references/ directory."""
    refs_dir = project_root / "Delagrave" / "references"
    assert refs_dir.exists(), f"References directory not found: {refs_dir}"
    return refs_dir


@pytest.fixture(scope="session")
def template_path(project_root):
    """Return path to the PowerPoint template file."""
    template = project_root / "Delagrave" / "Modele fiches - Powerpoint" / "Modèle fiche technique vide - Ind J.potm"
    assert template.exists(), f"Template file not found: {template}"
    return template


@pytest.fixture(scope="session")
def output_dir(project_root):
    """Return path to tests/output/ directory, creating it if needed."""
    out_dir = project_root / "tests" / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


@pytest.fixture(scope="session")
def sample_codes():
    """Return a dict mapping family names to known valid product codes."""
    return {
        'paillasse': 'PCD-A-60',
        'sorbonne': 'S-A',
        'revetement': 'DA',
        'meubles': 'ACB120',
        'tables-en': 'ELE',
        'equipement': '2CU12G',
        'elec-sorb': 'BARRIEREIMMAT',
        'complements': 'x',
        'enceinte-ventilee': 'SFC-209',
    }
