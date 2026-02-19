"""Adapter registry for QMeter XML parsing."""
from __future__ import annotations

import logging
from typing import Dict, List, Optional, Type

from .base import BaseAdapter

logger = logging.getLogger(__name__)

_REGISTRY: Dict[str, Type[BaseAdapter]] = {}


def register_adapter(name: str, adapter_cls: Type[BaseAdapter]) -> None:
    """Register an adapter class."""
    _REGISTRY[name] = adapter_cls
    logger.debug("Registered adapter: %s", name)


def get_adapter(name: str) -> Optional[Type[BaseAdapter]]:
    """Get an adapter class by name."""
    return _REGISTRY.get(name)


def detect_and_parse(filepath: str, source_zip: Optional[str] = None,
                     internal_path: str = "") -> Optional[object]:
    """Try each registered adapter in priority order until one succeeds."""
    # Priority order: v1 (Machine schema), v2 (log entries), fallback
    priority = ["adapter_v1", "adapter_v2", "adapter_fallback"]

    for name in priority:
        adapter_cls = _REGISTRY.get(name)
        if adapter_cls is None:
            continue
        adapter = adapter_cls()
        if adapter.can_parse(filepath):
            logger.info("Using %s for %s", name, filepath)
            result = adapter.parse(filepath, source_zip=source_zip,
                                   internal_path=internal_path)
            if result is not None:
                return result
            logger.warning("%s claimed to parse %s but returned None", name, filepath)

    logger.warning("No adapter could parse: %s", filepath)
    return None


def list_adapters() -> List[str]:
    """List registered adapter names."""
    return list(_REGISTRY.keys())
