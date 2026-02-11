"""Unit tests for PipelineLogger."""

import time
from pathlib import Path
from gendoc.utils.pipeline_logger import PipelineLogger


def test_logger_creates_log_file(tmp_path):
    """Test that logger creates a log file in the correct location."""
    logger = PipelineLogger(tmp_path)
    step = logger.start_step("Test step")
    logger.end_step(step)

    log_path = logger.write_log()

    assert log_path.exists()
    assert log_path.parent == tmp_path / "logs"
    assert log_path.suffix == ".md"


def test_log_file_name_format(tmp_path):
    """Test that log filename matches the expected pattern."""
    logger = PipelineLogger(tmp_path)
    log_path = logger.write_log()

    # Filename should be YYYYMMDD_HHMMSS_pipeline.md
    filename = log_path.name
    assert filename.endswith("_pipeline.md")

    # Extract timestamp part
    timestamp_part = filename.replace("_pipeline.md", "")
    assert len(timestamp_part) == 15  # YYYYMMDD_HHMMSS
    assert timestamp_part[8] == "_"  # Underscore separator


def test_log_contains_all_sections(tmp_path):
    """Test that log contains all 5 required French section headers."""
    logger = PipelineLogger(tmp_path)
    logger.set_input_params(test_param="test_value")

    step1 = logger.start_step("Test step")
    logger.end_step(step1)

    logger.log_error("Test error", context={"key": "value"})
    logger.log_solution("Test error", "Test solution")

    log_path = logger.write_log()
    content = log_path.read_text(encoding='utf-8')

    # Check all 5 REQUIRED exact French headers
    assert "# Log d'Execution Pipeline" in content
    assert "## Parametres d'Entree" in content
    assert "## Etapes du Pipeline" in content
    assert "## Erreurs Rencontrees" in content
    assert "## Solutions Appliquees" in content


def test_input_params_logged(tmp_path):
    """Test that input parameters appear in the log."""
    logger = PipelineLogger(tmp_path)
    logger.set_input_params(
        pdf_path="/path/to/file.pdf",
        product_codes=["CODE1", "CODE2"]
    )

    log_path = logger.write_log()
    content = log_path.read_text(encoding='utf-8')

    assert "pdf_path" in content
    assert "/path/to/file.pdf" in content
    assert "product_codes" in content
    assert "CODE1" in content or "['CODE1', 'CODE2']" in content


def test_step_duration_recorded(tmp_path):
    """Test that step duration is recorded and appears in output."""
    logger = PipelineLogger(tmp_path)

    step = logger.start_step("Slow step")
    time.sleep(0.05)  # Sleep for 50ms
    logger.end_step(step)

    log_path = logger.write_log()
    content = log_path.read_text(encoding='utf-8')

    # Duration should be > 0 and appear in the log
    assert "Slow step -- OK" in content
    # Check for duration format (e.g., "0.05s" or similar)
    assert "0.0" in content  # At least some duration value


def test_error_with_context_logged(tmp_path):
    """Test that errors with context are logged correctly."""
    logger = PipelineLogger(tmp_path)

    logger.log_error(
        "Test error message",
        context={"product_code": "TEST123", "file_path": "/path/to/file"}
    )

    log_path = logger.write_log()
    content = log_path.read_text(encoding='utf-8')

    assert "Test error message" in content
    assert "product_code" in content
    assert "TEST123" in content
    assert "file_path" in content
    assert "/path/to/file" in content


def test_solution_logged(tmp_path):
    """Test that solutions are logged with auto-resolved status."""
    logger = PipelineLogger(tmp_path)

    logger.log_error("Missing image file")
    logger.log_solution(
        "Missing image file",
        "Used placeholder image instead",
        auto_resolved=True
    )

    log_path = logger.write_log()
    content = log_path.read_text(encoding='utf-8')

    assert "Missing image file" in content
    assert "Used placeholder image instead" in content
    assert "automatique" in content


def test_failed_step_logged(tmp_path):
    """Test that failed steps show ECHOUE status and error appears in Errors section."""
    logger = PipelineLogger(tmp_path)

    step = logger.start_step("Failed step")
    logger.fail_step(
        step,
        "Something went wrong",
        traceback_str="Traceback (most recent call last):\n  File test.py, line 1\nError",
        context={"code": "TEST"}
    )

    log_path = logger.write_log()
    content = log_path.read_text(encoding='utf-8')

    assert "Failed step -- ECHOUE" in content
    assert "Something went wrong" in content
    assert "Traceback" in content
    assert "TEST" in content


def test_interrupted_step(tmp_path):
    """Test that interrupted steps (started but not ended) show INTERROMPU status."""
    logger = PipelineLogger(tmp_path)

    step1 = logger.start_step("Complete step")
    logger.end_step(step1)

    step2 = logger.start_step("Interrupted step")
    # Don't call end_step or fail_step

    log_path = logger.write_log()
    content = log_path.read_text(encoding='utf-8')

    assert "Complete step -- OK" in content
    assert "Interrupted step -- INTERROMPU" in content


def test_overall_status_ok(tmp_path):
    """Test that overall status is OK when all steps succeed and no errors."""
    logger = PipelineLogger(tmp_path)

    step1 = logger.start_step("Step 1")
    logger.end_step(step1)

    step2 = logger.start_step("Step 2")
    logger.end_step(step2)

    log_path = logger.write_log()
    content = log_path.read_text(encoding='utf-8')

    assert "**Statut:** OK" in content


def test_overall_status_errors(tmp_path):
    """Test that overall status is ERREURS when errors exist but pipeline completed."""
    logger = PipelineLogger(tmp_path)

    step1 = logger.start_step("Step 1")
    logger.end_step(step1)

    # Log an error without failing a step
    logger.log_error("Non-critical error", context={"code": "TEST"})

    step2 = logger.start_step("Step 2")
    logger.end_step(step2)

    log_path = logger.write_log()
    content = log_path.read_text(encoding='utf-8')

    assert "**Statut:** ERREURS" in content


def test_overall_status_failed(tmp_path):
    """Test that overall status is ECHOUE when a step fails."""
    logger = PipelineLogger(tmp_path)

    step1 = logger.start_step("Step 1")
    logger.end_step(step1)

    step2 = logger.start_step("Step 2")
    logger.fail_step(step2, "Critical failure")

    log_path = logger.write_log()
    content = log_path.read_text(encoding='utf-8')

    assert "**Statut:** ECHOUE" in content


def test_empty_pipeline(tmp_path):
    """Test that an empty pipeline produces a valid log file."""
    logger = PipelineLogger(tmp_path)

    log_path = logger.write_log()
    content = log_path.read_text(encoding='utf-8')

    # Should still have all sections
    assert "# Log d'Execution Pipeline" in content
    assert "## Parametres d'Entree" in content
    assert "## Etapes du Pipeline" in content
    assert "## Erreurs Rencontrees" in content
    assert "## Solutions Appliquees" in content

    # Should indicate nothing was logged
    assert "(Aucun parametre enregistre)" in content or "(Aucune etape enregistree)" in content


def test_write_log_idempotent(tmp_path):
    """Test that write_log can be called multiple times safely."""
    logger = PipelineLogger(tmp_path)

    step = logger.start_step("Test step")
    logger.end_step(step)

    # Call write_log twice
    log_path1 = logger.write_log()
    log_path2 = logger.write_log()

    # Both should succeed and point to the same file
    assert log_path1 == log_path2
    assert log_path1.exists()

    # Content should be the same
    content1 = log_path1.read_text(encoding='utf-8')
    content2 = log_path2.read_text(encoding='utf-8')
    assert content1 == content2


def test_step_result_data_logged(tmp_path):
    """Test that step result data appears in the log."""
    logger = PipelineLogger(tmp_path)

    step = logger.start_step("Analysis step")
    logger.end_step(step, result={
        "references": 42,
        "revetements": 5,
        "total_products": 47
    })

    log_path = logger.write_log()
    content = log_path.read_text(encoding='utf-8')

    assert "references" in content
    assert "42" in content
    assert "revetements" in content
    assert "5" in content
    assert "total_products" in content
    assert "47" in content
