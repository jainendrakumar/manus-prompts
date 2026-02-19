"""Ingestion module: handles ZIP extraction and XML file discovery."""
from __future__ import annotations

import glob
import logging
import os
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .adapters import detect_and_parse
from .models import AnalysisContext, LogEntry, QMeterResult

logger = logging.getLogger(__name__)


def _derive_label_from_path(path: str) -> str:
    """Derive a human-readable label from a file path or ZIP name."""
    basename = os.path.basename(path)
    name = os.path.splitext(basename)[0]
    # Clean up common patterns
    name = re.sub(r"_\d{8}$", "", name)  # Remove date suffixes
    name = re.sub(r"[-_]+", " ", name)
    return name.strip()


def _extract_zip(zip_path: str, extract_dir: str) -> List[str]:
    """Extract a ZIP file and return list of XML file paths."""
    xml_files = []
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)
            for root, dirs, files in os.walk(extract_dir):
                for f in sorted(files):
                    if f.lower().endswith(".xml"):
                        xml_files.append(os.path.join(root, f))
    except zipfile.BadZipFile as e:
        logger.error("Bad ZIP file %s: %s", zip_path, e)
    except Exception as e:
        logger.error("Error extracting %s: %s", zip_path, e)
    return xml_files


def _natural_sort_key(path: str):
    """Sort key for natural ordering of filenames (Run1, Run2, ..., Run10)."""
    basename = os.path.basename(path)
    parts = re.split(r"(\d+)", basename)
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def ingest_inputs(
    input_paths: List[str],
    label_map: Optional[Dict[str, str]] = None,
) -> AnalysisContext:
    """Ingest multiple ZIP and XML files into an AnalysisContext.

    Args:
        input_paths: List of paths to ZIP files, XML files, or glob patterns.
        label_map: Optional mapping of source names to labels.

    Returns:
        AnalysisContext with all parsed results.
    """
    if label_map is None:
        label_map = {}

    context = AnalysisContext(label_map=label_map)
    temp_dirs: List[str] = []

    # Expand globs
    expanded_paths: List[str] = []
    for p in input_paths:
        matches = glob.glob(p)
        if matches:
            expanded_paths.extend(sorted(matches))
        else:
            expanded_paths.append(p)

    try:
        for input_path in expanded_paths:
            if not os.path.exists(input_path):
                logger.warning("Input path does not exist: %s", input_path)
                context.warnings.append(f"Input not found: {input_path}")
                continue

            source_name = os.path.basename(input_path)
            source_label = label_map.get(
                source_name,
                _derive_label_from_path(input_path)
            )

            if input_path.lower().endswith(".zip"):
                _process_zip(input_path, source_label, context, temp_dirs)
            elif input_path.lower().endswith(".xml"):
                _process_xml(input_path, None, input_path, source_label, context)
            else:
                logger.warning("Unsupported file type: %s", input_path)
                context.warnings.append(f"Unsupported file: {input_path}")
    finally:
        # Clean up temp directories
        for td in temp_dirs:
            try:
                shutil.rmtree(td, ignore_errors=True)
            except Exception:
                pass

    logger.info(
        "Ingestion complete: %d results, %d log entries, %d warnings",
        len(context.results), len(context.log_entries), len(context.warnings),
    )
    return context


def _process_zip(
    zip_path: str,
    source_label: str,
    context: AnalysisContext,
    temp_dirs: List[str],
) -> None:
    """Process a ZIP file."""
    temp_dir = tempfile.mkdtemp(prefix="qmeter_")
    temp_dirs.append(temp_dir)

    xml_files = _extract_zip(zip_path, temp_dir)
    if not xml_files:
        context.warnings.append(f"No XML files found in {zip_path}")
        return

    logger.info("Found %d XML files in %s", len(xml_files), zip_path)

    # Sort naturally
    xml_files.sort(key=_natural_sort_key)

    zip_name = os.path.basename(zip_path)
    for xml_path in xml_files:
        rel_path = os.path.relpath(xml_path, temp_dir)
        _process_xml(xml_path, zip_name, rel_path, source_label, context)


def _process_xml(
    xml_path: str,
    source_zip: Optional[str],
    internal_path: str,
    source_label: str,
    context: AnalysisContext,
) -> None:
    """Process a single XML file."""
    result = detect_and_parse(
        xml_path,
        source_zip=source_zip,
        internal_path=internal_path,
    )

    if result is None:
        return

    if isinstance(result, QMeterResult):
        result.source_label = source_label
        result.label = _make_run_label(result, source_label)
        context.results.append(result)
    elif isinstance(result, list):
        if result and isinstance(result[0], LogEntry):
            context.log_entries.extend(result)
        else:
            for r in result:
                if isinstance(r, QMeterResult):
                    r.source_label = source_label
                    r.label = _make_run_label(r, source_label)
                    context.results.append(r)
    else:
        logger.warning("Unexpected result type from adapter: %s", type(result))


def _make_run_label(result: QMeterResult, source_label: str) -> str:
    """Create a descriptive label for a run result."""
    machine = result.machine.name or "Unknown"
    parts = [source_label]
    if result.runs:
        run = result.runs[0]
        parts.append(f"Run{run.run_number}")
    parts.append(machine)
    return " / ".join(parts)
