"""Adapter V1: Machine/Run/Category/Group/Task XML schema.

This is the primary QMeter export format used by most XML files.
"""
from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from typing import List, Optional, Union

from .base import BaseAdapter
from ..models import (
    CategoryRecord, GroupRecord, MachineInfo, Provenance,
    QMeterResult, RunRecord, TaskRecord,
)
from ..utils.numeric import parse_iso_duration, safe_float, safe_int

logger = logging.getLogger(__name__)


class AdapterV1(BaseAdapter):
    """Parse Machine/Run/Category/Group/Task XML files."""

    def can_parse(self, filepath: str) -> bool:
        """Check if root element is <Machine> with expected attributes."""
        try:
            for event, elem in ET.iterparse(filepath, events=["start"]):
                if elem.tag == "Machine" and "Name" in elem.attrib:
                    return True
                return False  # First element is not Machine
        except (ET.ParseError, Exception):
            return False
        return False

    def parse(self, filepath: str, source_zip: Optional[str] = None,
              internal_path: str = "") -> Optional[Union[QMeterResult, List[QMeterResult]]]:
        """Parse a Machine XML file."""
        try:
            tree = ET.parse(filepath)
        except ET.ParseError as e:
            logger.error("XML parse error in %s: %s", filepath, e)
            return None

        root = tree.getroot()
        if root.tag != "Machine":
            return None

        machine = MachineInfo.from_xml_attribs(root.attrib)
        provenance = Provenance(
            source_zip=source_zip,
            internal_path=internal_path or filepath,
            file_hash=Provenance.compute_hash(filepath),
            adapter_used="adapter_v1",
        )

        warnings: List[str] = []
        runs: List[RunRecord] = []

        for run_elem in root.findall("Run"):
            run = RunRecord.from_xml_attribs(run_elem.attrib)
            categories: List[CategoryRecord] = []

            for cat_elem in run_elem.findall("Category"):
                cat = CategoryRecord(
                    number=safe_int(cat_elem.get("Number", "0")),
                    name=cat_elem.get("Name", "Unknown"),
                    avg_runtime=safe_float(
                        cat_elem.get("AvgRuntime", "0"),
                        context=f"Category {cat_elem.get('Number')} AvgRuntime"
                    ),
                    groups=[],
                )

                for grp_elem in cat_elem.findall("Group"):
                    grp = GroupRecord(
                        number=safe_int(grp_elem.get("Number", "0")),
                        nr_of_threads=safe_int(grp_elem.get("NrOfThreads", "1")),
                        group_score=safe_float(
                            grp_elem.get("GroupScore", "0"),
                            context=f"Group {grp_elem.get('Number')} GroupScore"
                        ),
                        avg_runtime=safe_float(
                            grp_elem.get("AvgRuntime", "0"),
                            context=f"Group {grp_elem.get('Number')} AvgRuntime"
                        ),
                        std_dev_runtime=safe_float(
                            grp_elem.get("StdDevRuntime", "0"),
                            context=f"Group {grp_elem.get('Number')} StdDevRuntime"
                        ),
                        tasks=[],
                    )

                    for task_elem in grp_elem.findall("Task"):
                        duration_ms = parse_iso_duration(
                            task_elem.get("Duration", "")
                        )
                        if duration_ms is None:
                            warnings.append(
                                f"Could not parse duration for task "
                                f"{task_elem.get('ID', '?')} in {filepath}"
                            )
                            duration_ms = 0.0

                        task = TaskRecord(
                            task_id=task_elem.get("ID", ""),
                            thread=safe_int(task_elem.get("Thread", "0")),
                            duration_seconds=duration_ms / 1000.0,
                            start=task_elem.get("Start"),
                            end=task_elem.get("End"),
                            precision_start=safe_int(
                                task_elem.get("PrecisionStart", "0")
                            ) or None,
                            precision_end=safe_int(
                                task_elem.get("PrecisionEnd", "0")
                            ) or None,
                            precision_frequency=safe_int(
                                task_elem.get("PrecisionFrequency", "0")
                            ) or None,
                        )
                        grp.tasks.append(task)

                    cat.groups.append(grp)
                categories.append(cat)

            run.categories = categories
            runs.append(run)

        if not runs:
            warnings.append(f"No Run elements found in {filepath}")
            return None

        result = QMeterResult(
            machine=machine,
            runs=runs,
            provenance=provenance,
            warnings=warnings,
        )
        return result
