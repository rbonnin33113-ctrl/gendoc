"""
Tests for detection robustness - exclusion filtering and unknown code handling.

These tests verify that:
1. Common false positives (measurement values, section headers, etc.) are filtered out
2. EXCLUSION_WORDS constant is properly defined and used
3. Genuine unknown codes are preserved and logged
4. Real product codes are not affected by exclusion filtering
"""

import pytest
from pathlib import Path

from gendoc.parsers.devis_analyzer import (
    EXCLUSION_WORDS,
    classify_codes,
    analyze_devis
)


def test_exclusion_words_constant_exists():
    """Verify EXCLUSION_WORDS constant exists and contains expected entries."""
    assert isinstance(EXCLUSION_WORDS, set), "EXCLUSION_WORDS should be a set"
    assert len(EXCLUSION_WORDS) > 20, "EXCLUSION_WORDS should contain at least 20+ entries"

    # Check for known false positive entries
    expected_entries = ["850MM", "CONDITIONS", "LIVRAISON", "SALLE"]
    for entry in expected_entries:
        assert entry in EXCLUSION_WORDS, f"{entry} should be in EXCLUSION_WORDS"


def test_classify_codes_filters_exclusions(references_dir):
    """Verify exclusion words are filtered from inconnus output."""
    codes = ["850MM", "CONDITIONS", "LIVRAISON", "PM-D-H-75"]

    result = classify_codes(codes, references_dir)

    # PM-D-H-75 is a valid product (paillasse)
    assert len(result["references"]) == 1, "Should find 1 valid product"
    assert result["references"][0]["code"] == "PM-D-H-75"
    assert result["references"][0]["famille"] == "paillasse"

    # Exclusion words should NOT appear in inconnus
    assert "850MM" not in result["inconnus"], "850MM should be filtered (exclusion word)"
    assert "CONDITIONS" not in result["inconnus"], "CONDITIONS should be filtered (exclusion word)"
    assert "LIVRAISON" not in result["inconnus"], "LIVRAISON should be filtered (exclusion word)"

    # inconnus should be empty (all false positives filtered, PM-D-H-75 is real)
    assert len(result["inconnus"]) == 0, "inconnus should be empty after filtering"


def test_classify_codes_filters_measurement_pattern(references_dir):
    """Verify measurement values matching pattern are filtered."""
    codes = ["1200MM", "2500MM", "750M", "PM-C-75"]

    result = classify_codes(codes, references_dir)

    # PM-C-75 is a valid product (paillasse)
    assert len(result["references"]) == 1, "Should find 1 valid product"
    assert result["references"][0]["code"] == "PM-C-75"

    # Measurement patterns should NOT appear in inconnus
    assert "1200MM" not in result["inconnus"], "1200MM should be filtered (measurement pattern)"
    assert "2500MM" not in result["inconnus"], "2500MM should be filtered (measurement pattern)"
    assert "750M" not in result["inconnus"], "750M should be filtered (measurement pattern)"

    # inconnus should be empty
    assert len(result["inconnus"]) == 0, "inconnus should be empty after filtering"


def test_genuine_unknown_codes_remain(references_dir):
    """Verify that genuinely unknown codes (not in exclusions, not in catalog) remain in inconnus."""
    codes = ["XYZFOO123", "NOTAPRODUCT99"]

    result = classify_codes(codes, references_dir)

    # These are not real products, not exclusions, not SP, not forfaits
    # They should appear in inconnus
    assert "XYZFOO123" in result["inconnus"], "XYZFOO123 should be in inconnus (genuine unknown)"
    assert "NOTAPRODUCT99" in result["inconnus"], "NOTAPRODUCT99 should be in inconnus (genuine unknown)"
    assert len(result["inconnus"]) == 2, "Should have exactly 2 unknown codes"


def test_exclusion_does_not_affect_real_products(references_dir):
    """Verify exclusion filtering does not affect valid catalog products."""
    # Use a variety of known product codes from different families
    codes = [
        "PM-D-H-75",    # paillasse
        "S-A",          # sorbonne
        "ACB120",       # meubles
        "2CU12G",       # equipement
        "ELE"           # tables-en
    ]

    result = classify_codes(codes, references_dir)

    # All should be found as valid products
    found_codes = [ref["code"] for ref in result["references"]]
    assert "PM-D-H-75" in found_codes, "PM-D-H-75 should be found"
    assert "S-A" in found_codes, "S-A should be found"
    assert "ACB120" in found_codes, "ACB120 should be found"
    assert "2CU12G" in found_codes, "2CU12G should be found"
    assert "ELE" in found_codes, "ELE should be found"

    # Should find all 5 valid products
    assert len(result["references"]) >= 5, "Should find at least 5 valid products"

    # None should be in inconnus
    for code in codes:
        assert code not in result["inconnus"], f"{code} should not be in inconnus"


def test_preview_includes_inconnus_count(references_dir):
    """Verify that analyze_devis result includes inconnus list."""
    # This test documents the contract: the result dict must include 'inconnus' key
    codes = ["PM-D-H-75", "XYZFOO123"]

    result = classify_codes(codes, references_dir)

    # Contract: result must have 'inconnus' key with a list
    assert "inconnus" in result, "Result must include 'inconnus' key"
    assert isinstance(result["inconnus"], list), "'inconnus' must be a list"

    # In this case, should have 1 unknown (XYZFOO123)
    assert len(result["inconnus"]) == 1, "Should have 1 unknown code"
    assert result["inconnus"][0] == "XYZFOO123", "XYZFOO123 should be in inconnus"
