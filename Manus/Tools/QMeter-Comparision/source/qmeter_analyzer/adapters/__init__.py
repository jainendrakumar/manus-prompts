"""QMeter XML adapters package."""
from .adapter_v1 import AdapterV1
from .adapter_v2 import AdapterV2
from .adapter_fallback import AdapterFallback
from .registry import register_adapter, detect_and_parse, list_adapters

# Register adapters on import
register_adapter("adapter_v1", AdapterV1)
register_adapter("adapter_v2", AdapterV2)
register_adapter("adapter_fallback", AdapterFallback)

__all__ = [
    "AdapterV1", "AdapterV2", "AdapterFallback",
    "register_adapter", "detect_and_parse", "list_adapters",
]
