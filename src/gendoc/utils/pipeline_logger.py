"""
Pipeline logger for gendoc - produces structured Markdown logs for every execution.

Creates timestamped .md log files in output/logs/ with complete diagnostic info:
- Execution summary with overall status
- Input parameters (PDF path, product codes, devis info)
- Pipeline steps with durations and outcomes
- Errors encountered with full context
- Solutions applied (auto-resolved or manual)

Purpose: Enable diagnostic transparency - when something fails or behaves unexpectedly,
the log file gives both humans and AI complete context to understand and fix the issue
without needing to reproduce the run.
"""

from pathlib import Path
from datetime import datetime
import time


class PipelineLogger:
    """Tracks a full pipeline execution and writes a structured Markdown log file.

    Usage:
        logger = PipelineLogger(output_dir)
        logger.set_input_params(pdf_path="...", product_codes=[...])

        step1 = logger.start_step("Analyse PDF")
        # ... do work ...
        logger.end_step(step1, result={"references": 10})

        step2 = logger.start_step("Generation PPTX")
        try:
            # ... do work ...
            logger.end_step(step2, result={"slides_generated": 5})
        except Exception as e:
            logger.fail_step(step2, str(e), traceback_str=traceback.format_exc())

        log_path = logger.write_log()
    """

    def __init__(self, output_dir: Path):
        """Initialize logger with output directory.

        Args:
            output_dir: Base output directory (logs will be in output_dir/logs/)
        """
        self.output_dir = Path(output_dir)
        self.log_dir = self.output_dir / "logs"
        self.start_time = datetime.now()
        self.start_perf = time.perf_counter()
        self.log_id = self.start_time.strftime("%Y%m%d_%H%M%S")

        # Storage
        self.steps = []
        self.errors = []
        self.solutions = []
        self.input_params = {}

        # Step tracking
        self._step_counter = 0
        self._active_steps = {}  # step_id -> (name, start_perf)

    def set_input_params(self, **kwargs):
        """Store arbitrary input parameters.

        Args:
            **kwargs: Key-value pairs to store (pdf_path, product_codes, devis_info, etc.)
        """
        self.input_params.update(kwargs)

    def start_step(self, name: str) -> str:
        """Record step start time.

        Args:
            name: Step name (e.g., "Analyse PDF", "Preview generation")

        Returns:
            step_id: Identifier to pass to end_step/fail_step
        """
        self._step_counter += 1
        step_id = str(self._step_counter)
        start_perf = time.perf_counter()

        self._active_steps[step_id] = (name, start_perf)

        return step_id

    def end_step(self, step_id: str, result: dict = None):
        """Record successful step completion.

        Args:
            step_id: Step identifier from start_step
            result: Optional dict with result summary (key-value pairs)
        """
        if step_id not in self._active_steps:
            return

        name, start_perf = self._active_steps[step_id]
        end_perf = time.perf_counter()
        duration = end_perf - start_perf

        self.steps.append({
            "id": step_id,
            "name": name,
            "status": "OK",
            "duration": duration,
            "result": result or {}
        })

        del self._active_steps[step_id]

    def fail_step(self, step_id: str, error: str, traceback_str: str = None, context: dict = None):
        """Record step failure.

        Args:
            step_id: Step identifier from start_step
            error: Error message
            traceback_str: Optional full traceback
            context: Optional context dict (product_code, file_path, etc.)
        """
        if step_id not in self._active_steps:
            return

        name, start_perf = self._active_steps[step_id]
        end_perf = time.perf_counter()
        duration = end_perf - start_perf

        self.steps.append({
            "id": step_id,
            "name": name,
            "status": "ECHOUE",
            "duration": duration,
            "error": error,
            "traceback": traceback_str,
            "context": context or {}
        })

        # Also add to errors list
        self.log_error(error, context=context, traceback_str=traceback_str)

        del self._active_steps[step_id]

    def log_error(self, error: str, context: dict = None, traceback_str: str = None):
        """Log an error (non-step-specific or per-product error).

        Args:
            error: Error message
            context: Optional context dict (product_code, file_path, etc.)
            traceback_str: Optional traceback
        """
        self.errors.append({
            "error": error,
            "context": context or {},
            "traceback": traceback_str
        })

    def log_solution(self, error_ref: str, solution: str, auto_resolved: bool = True):
        """Log a resolution (automatic or manual).

        Args:
            error_ref: Reference to the error (description or identifier)
            solution: Description of the solution applied
            auto_resolved: Whether it was automatically resolved (default True)
        """
        self.solutions.append({
            "error_ref": error_ref,
            "solution": solution,
            "auto_resolved": auto_resolved
        })

    def write_log(self) -> Path:
        """Write the Markdown log file.

        Creates logs directory if needed, writes {log_id}_pipeline.md with all
        tracked data, returns the path to the written file.

        Returns:
            Path to the written log file
        """
        # Create logs directory
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Calculate total duration
        end_perf = time.perf_counter()
        total_duration = end_perf - self.start_perf

        # Mark any active steps as interrupted
        for step_id, (name, start_perf) in self._active_steps.items():
            duration = end_perf - start_perf
            self.steps.append({
                "id": step_id,
                "name": name,
                "status": "INTERROMPU",
                "duration": duration
            })
        self._active_steps.clear()

        # Determine overall status
        has_failed_steps = any(s["status"] == "ECHOUE" for s in self.steps)
        has_errors = len(self.errors) > 0
        has_successful_steps = any(s["status"] == "OK" for s in self.steps)

        if has_failed_steps:
            overall_status = "ECHOUE"
        elif has_errors and has_successful_steps:
            overall_status = "ERREURS"
        elif has_errors:
            overall_status = "ECHOUE"
        elif has_successful_steps:
            overall_status = "OK"
        else:
            overall_status = "OK"

        # Build Markdown content
        md_lines = []

        # Title and status (REQUIRED EXACT HEADER)
        md_lines.append("# Log d'Execution Pipeline")
        md_lines.append("")
        md_lines.append(f"**Statut:** {overall_status}")
        md_lines.append(f"**Date:** {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        md_lines.append(f"**Duree totale:** {total_duration:.2f}s")
        md_lines.append("")

        # Input Parameters section (REQUIRED EXACT HEADER)
        md_lines.append("## Parametres d'Entree")
        md_lines.append("")
        if self.input_params:
            for key, value in self.input_params.items():
                # Format value based on type
                if isinstance(value, (list, dict)):
                    value_str = str(value)
                    if len(value_str) > 100:
                        value_str = value_str[:100] + "..."
                else:
                    value_str = str(value)
                md_lines.append(f"- **{key}:** {value_str}")
            md_lines.append("")
        else:
            md_lines.append("*(Aucun parametre enregistre)*")
            md_lines.append("")

        # Pipeline Steps section (REQUIRED EXACT HEADER)
        md_lines.append("## Etapes du Pipeline")
        md_lines.append("")
        if self.steps:
            for step in self.steps:
                step_num = step["id"]
                step_name = step["name"]
                step_status = step["status"]
                step_duration = step["duration"]

                md_lines.append(f"### {step_num}. {step_name} -- {step_status} ({step_duration:.2f}s)")
                md_lines.append("")

                # Add result data if present
                if "result" in step and step["result"]:
                    for key, value in step["result"].items():
                        md_lines.append(f"- **{key}:** {value}")
                    md_lines.append("")

                # Add error info if failed
                if step["status"] == "ECHOUE" and "error" in step:
                    md_lines.append(f"**Erreur:** {step['error']}")
                    md_lines.append("")

                    if step.get("context"):
                        md_lines.append("**Contexte:**")
                        for key, value in step["context"].items():
                            md_lines.append(f"- **{key}:** {value}")
                        md_lines.append("")

                    if step.get("traceback"):
                        md_lines.append("**Traceback:**")
                        md_lines.append("```")
                        md_lines.append(step["traceback"])
                        md_lines.append("```")
                        md_lines.append("")
        else:
            md_lines.append("*(Aucune etape enregistree)*")
            md_lines.append("")

        # Errors section (REQUIRED EXACT HEADER)
        md_lines.append("## Erreurs Rencontrees")
        md_lines.append("")
        if self.errors:
            for idx, err in enumerate(self.errors, 1):
                md_lines.append(f"### Erreur {idx}")
                md_lines.append("")
                md_lines.append(f"**Message:** {err['error']}")
                md_lines.append("")

                if err.get("context"):
                    md_lines.append("**Contexte:**")
                    for key, value in err["context"].items():
                        md_lines.append(f"- **{key}:** {value}")
                    md_lines.append("")

                if err.get("traceback"):
                    md_lines.append("**Traceback:**")
                    md_lines.append("```")
                    md_lines.append(err["traceback"])
                    md_lines.append("```")
                    md_lines.append("")
        else:
            md_lines.append("*(Aucune erreur rencontree)*")
            md_lines.append("")

        # Solutions section (REQUIRED EXACT HEADER)
        md_lines.append("## Solutions Appliquees")
        md_lines.append("")
        if self.solutions:
            for idx, sol in enumerate(self.solutions, 1):
                md_lines.append(f"### Solution {idx}")
                md_lines.append("")
                md_lines.append(f"**Probleme:** {sol['error_ref']}")
                md_lines.append("")
                md_lines.append(f"**Solution:** {sol['solution']}")
                md_lines.append("")
                status = "automatique" if sol["auto_resolved"] else "manuelle"
                md_lines.append(f"**Resolution:** {status}")
                md_lines.append("")
        else:
            md_lines.append("*(Aucune solution enregistree)*")
            md_lines.append("")

        # Write file
        log_filename = f"{self.log_id}_pipeline.md"
        log_path = self.log_dir / log_filename

        with open(log_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(md_lines))

        return log_path
