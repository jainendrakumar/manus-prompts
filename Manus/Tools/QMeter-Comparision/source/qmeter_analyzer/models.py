"""Data models for QMeter Analyzer."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TaskRecord:
    """Individual task measurement within a group."""
    task_id: str
    thread: int
    duration_seconds: float
    start: Optional[str] = None
    end: Optional[str] = None
    precision_start: Optional[int] = None
    precision_end: Optional[int] = None
    precision_frequency: Optional[int] = None


@dataclass
class GroupRecord:
    """A group of tasks run with a specific thread count."""
    number: int
    nr_of_threads: int
    group_score: float
    avg_runtime: float
    std_dev_runtime: float
    tasks: List[TaskRecord] = field(default_factory=list)


@dataclass
class CategoryRecord:
    """A test category (Memory, Algorithm, Quill, Propagator, Database)."""
    number: int
    name: str
    avg_runtime: float
    groups: List[GroupRecord] = field(default_factory=list)


@dataclass
class MachineInfo:
    """Hardware and software information about the test machine."""
    name: str = ""
    cpu_name: str = ""
    cpu_max_clock_speed: int = 0
    cpu_nr_of_logical_cores: int = 0
    cpu_nr_of_physical_cores: int = 0
    cpu_number_of_processors: int = 0
    cpu_is_hyper_threaded: bool = False
    cpu_l2_cache: int = 0
    cpu_l3_cache: int = 0
    total_memory_mb: int = 0
    available_memory_mb: int = 0
    computer_model: str = ""
    computer_os: str = ""
    computer_system_type: str = ""
    qmeter_version: str = ""
    quintiq_version: str = ""
    hw_type: str = ""
    motherboard_manufacturer: str = ""
    motherboard_product: str = ""
    numa_nodes: str = ""
    export_comment: str = ""
    current_date: str = ""

    @classmethod
    def from_xml_attribs(cls, attribs: Dict[str, str]) -> "MachineInfo":
        """Create MachineInfo from XML Machine element attributes."""
        def _int(key: str, default: int = 0) -> int:
            val = attribs.get(key, str(default))
            try:
                return int(val)
            except (ValueError, TypeError):
                return default

        def _bool(key: str) -> bool:
            return attribs.get(key, "false").lower() == "true"

        return cls(
            name=attribs.get("Name", ""),
            cpu_name=attribs.get("CPU_Name", "").strip(),
            cpu_max_clock_speed=_int("CPU_MaxClockSpeed"),
            cpu_nr_of_logical_cores=_int("CPU_NrOfLogicalCores"),
            cpu_nr_of_physical_cores=_int("CPU_NrOfPhysicalCores"),
            cpu_number_of_processors=_int("CPU_NumberOfProcessors"),
            cpu_is_hyper_threaded=_bool("CPU_IsHyperThreaded"),
            cpu_l2_cache=_int("CPU_L2_Cache"),
            cpu_l3_cache=_int("CPU_L3_Cache"),
            total_memory_mb=_int("TotalMemory_MB"),
            available_memory_mb=_int("AvailableMemory_MB"),
            computer_model=attribs.get("Computer_Model", ""),
            computer_os=attribs.get("Computer_OperatingSystem", ""),
            computer_system_type=attribs.get("Computer_SystemType", ""),
            qmeter_version=attribs.get("Computer_QMeterVersion", ""),
            quintiq_version=attribs.get("Computer_QuintiqVersion", ""),
            hw_type=attribs.get("HW_Type", ""),
            motherboard_manufacturer=attribs.get("Motherboard_Manufacturer", ""),
            motherboard_product=attribs.get("Motherboard_Product", ""),
            numa_nodes=attribs.get("NUMA_nodes", ""),
            export_comment=attribs.get("Export_Comment", ""),
            current_date=attribs.get("Computer_CurrentDate", ""),
        )


@dataclass
class RunRecord:
    """A single QMeter run with scores and categories."""
    run_number: int
    score1: Optional[float] = None
    score4: Optional[float] = None
    score16: Optional[float] = None
    config_categories: str = ""
    config_lite_mode: bool = False
    config_timeout: int = 600
    config_max_datasets: int = 16
    config_min_datasets: int = 1
    categories: List[CategoryRecord] = field(default_factory=list)

    @classmethod
    def from_xml_attribs(cls, attribs: Dict[str, str]) -> "RunRecord":
        """Create RunRecord from XML Run element attributes."""
        def _float_opt(key: str) -> Optional[float]:
            val = attribs.get(key)
            if val is None:
                return None
            try:
                return float(val.replace(",", ""))
            except (ValueError, TypeError):
                return None

        def _int(key: str, default: int = 0) -> int:
            val = attribs.get(key, str(default))
            try:
                return int(val)
            except (ValueError, TypeError):
                return default

        return cls(
            run_number=_int("Number", 1),
            score1=_float_opt("Score1"),
            score4=_float_opt("Score4"),
            score16=_float_opt("Score16"),
            config_categories=attribs.get("Config_Categories", ""),
            config_lite_mode=attribs.get("Config_LiteMode", "false").lower() == "true",
            config_timeout=_int("Config_Timeout", 600),
            config_max_datasets=_int("Config_MaxDatasets", 16),
            config_min_datasets=_int("Config_MinDatasets", 1),
        )


@dataclass
class Provenance:
    """Tracks the origin of a parsed file."""
    source_zip: Optional[str] = None
    internal_path: str = ""
    file_hash: str = ""
    adapter_used: str = ""

    @staticmethod
    def compute_hash(filepath: str) -> str:
        """Compute SHA-256 hash of a file."""
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()


@dataclass
class QMeterResult:
    """Complete parsed result from a single XML file."""
    machine: MachineInfo
    runs: List[RunRecord]
    provenance: Provenance
    label: str = ""
    source_label: str = ""
    warnings: List[str] = field(default_factory=list)


@dataclass
class LogEntry:
    """A log entry from qmeter_results.xml format."""
    datetime: str = ""
    category: Optional[int] = None
    dataset: Optional[int] = None
    duration_seconds: Optional[float] = None
    precision_start: Optional[str] = None
    precision_end: Optional[str] = None
    precision_frequency: Optional[str] = None
    message: Optional[str] = None


@dataclass
class AnalysisContext:
    """Container for all parsed results and analysis configuration."""
    results: List[QMeterResult] = field(default_factory=list)
    log_entries: List[LogEntry] = field(default_factory=list)
    baseline_index: int = 0
    label_map: Dict[str, str] = field(default_factory=dict)
    metric_rules: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
