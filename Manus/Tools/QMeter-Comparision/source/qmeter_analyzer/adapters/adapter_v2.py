"""Adapter V2: Root/logentry XML schema (qmeter_results.xml format).

This format contains log entries with category, dataset, and duration information.
"""
from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from typing import List, Optional, Union

from .base import BaseAdapter
from ..models import LogEntry, Provenance, QMeterResult

logger = logging.getLogger(__name__)


class AdapterV2(BaseAdapter):
    """Parse Root/logentry XML files (qmeter_results.xml)."""

    def can_parse(self, filepath: str) -> bool:
        """Check if root element is <Root> with <logentry> children."""
        try:
            for event, elem in ET.iterparse(filepath, events=["start"]):
                if elem.tag == "Root":
                    return True
                return False
        except (ET.ParseError, Exception):
            return False
        return False

    def parse(self, filepath: str, source_zip: Optional[str] = None,
              internal_path: str = "") -> Optional[List[LogEntry]]:
        """Parse a log-entry XML file and return list of LogEntry objects."""
        try:
            tree = ET.parse(filepath)
        except ET.ParseError as e:
            logger.error("XML parse error in %s: %s", filepath, e)
            return None

        root = tree.getroot()
        if root.tag != "Root":
            return None

        entries: List[LogEntry] = []
        for entry_elem in root.findall("logentry"):
            entry = LogEntry()

            dt_elem = entry_elem.find("datetime")
            if dt_elem is not None and dt_elem.text:
                entry.datetime = dt_elem.text.strip()

            cat_elem = entry_elem.find("category")
            if cat_elem is not None and cat_elem.text:
                try:
                    entry.category = int(cat_elem.text.strip())
                except ValueError:
                    pass

            ds_elem = entry_elem.find("dataset")
            if ds_elem is not None and ds_elem.text:
                try:
                    entry.dataset = int(ds_elem.text.strip())
                except ValueError:
                    pass

            dur_elem = entry_elem.find("duration_seconds")
            if dur_elem is not None and dur_elem.text:
                val = dur_elem.text.strip()
                if val.lower() not in ("n/a", "na", ""):
                    try:
                        entry.duration_seconds = float(val)
                    except ValueError:
                        pass

            for field in ("precision_start", "precision_end", "precision_frequency"):
                elem = entry_elem.find(field)
                if elem is not None and elem.text:
                    setattr(entry, field, elem.text.strip())

            msg_elem = entry_elem.find("message")
            if msg_elem is not None and msg_elem.text:
                entry.message = msg_elem.text.strip()

            entries.append(entry)

        logger.info("Parsed %d log entries from %s", len(entries), filepath)
        return entries if entries else None
