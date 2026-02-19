"""Base adapter interface for QMeter XML parsing."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Union

from ..models import QMeterResult


class BaseAdapter(ABC):
    """Abstract base class for XML adapters."""

    @abstractmethod
    def can_parse(self, filepath: str) -> bool:
        """Check if this adapter can parse the given file."""
        ...

    @abstractmethod
    def parse(self, filepath: str, source_zip: Optional[str] = None,
              internal_path: str = "") -> Optional[Union[QMeterResult, list]]:
        """Parse the file and return QMeterResult(s) or None on failure."""
        ...
