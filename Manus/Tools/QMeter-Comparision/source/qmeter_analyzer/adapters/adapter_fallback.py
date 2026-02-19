"""Adapter Fallback: Attempts to extract any useful data from unknown XML schemas."""
from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from typing import Optional, Union

from .base import BaseAdapter
from ..models import QMeterResult

logger = logging.getLogger(__name__)


class AdapterFallback(BaseAdapter):
    """Fallback adapter that logs unrecognized XML files."""

    def can_parse(self, filepath: str) -> bool:
        """Accept any XML file as last resort."""
        try:
            ET.parse(filepath)
            return True
        except Exception:
            return False

    def parse(self, filepath: str, source_zip: Optional[str] = None,
              internal_path: str = "") -> Optional[QMeterResult]:
        """Log the unrecognized file and return None."""
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            logger.warning(
                "Fallback adapter: unrecognized schema in %s "
                "(root=%s, attribs=%s, children=%s)",
                filepath, root.tag,
                list(root.attrib.keys())[:5],
                [c.tag for c in list(root)[:5]],
            )
        except Exception as e:
            logger.error("Fallback adapter: cannot parse %s: %s", filepath, e)
        return None
