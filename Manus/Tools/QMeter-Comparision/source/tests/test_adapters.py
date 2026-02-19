"""Tests for XML adapters and comparison math."""
import os
import tempfile
import pytest
from qmeter_analyzer.adapters.adapter_v1 import AdapterV1
from qmeter_analyzer.adapters.adapter_v2 import AdapterV2
from qmeter_analyzer.adapters.adapter_fallback import AdapterFallback
from qmeter_analyzer.analytics.compare import compute_diff, get_directionality
from qmeter_analyzer.analytics.stability import compute_stability_stats, detect_outliers


# Sample XML for testing
SAMPLE_V1_XML = """<?xml version="1.0" encoding="utf-8"?>
<Machine Name="TestMachine" CPU_Name="Test CPU" CPU_MaxClockSpeed="3000"
         CPU_NrOfLogicalCores="8" CPU_NrOfPhysicalCores="4"
         CPU_NumberOfProcessors="1" CPU_IsHyperThreaded="true"
         CPU_L2_Cache="256" CPU_L3_Cache="8192"
         TotalMemory_MB="16384" AvailableMemory_MB="12000"
         Computer_Model="TestModel" Computer_OperatingSystem="TestOS"
         Computer_SystemType="x64" Computer_QMeterVersion="0.34"
         Computer_QuintiqVersion="6.4.9.0" HW_Type="Physical"
         Motherboard_Manufacturer="Test" Motherboard_Name="Board"
         Motherboard_Product="TestBoard" NUMA_nodes="1"
         Export_Comment="" Computer_CurrentDate="2026-01-01T00:00:00">
  <Run Number="1" Score1="50000" Score4="48000" Score16="45000"
       Config_Categories="1,2,3,4,5" Config_LiteMode="false"
       Config_Timeout="600" Config_MaxDatasets="16" Config_MinDatasets="1"
       Config_IsGoldScoreAltered="false" Config_RunOnStartup="false"
       LiteMode="false">
    <Category Name="Memory test" Number="1" AvgRuntime="5000">
      <Group Number="1" NrOfThreads="1" GroupScore="4500"
             AvgRuntime="4500" StdDevRuntime="0">
        <Task ID="DS-1-1-1" Thread="1" Duration="P0DT0H0M4.5S"
              Start="2026-01-01T00:00:00" End="2026-01-01T00:00:04.5"
              PrecisionStart="100" PrecisionEnd="200"
              PrecisionFrequency="1000000000"/>
      </Group>
    </Category>
  </Run>
</Machine>"""

SAMPLE_V2_XML = """<?xml version="1.0" encoding="utf-8"?>
<Root>
  <logentry>
    <datetime>2026-01-01 00:00:00</datetime>
    <category>1</category>
    <dataset>1</dataset>
    <precision_start>100</precision_start>
    <precision_end>200</precision_end>
    <precision_frequency>1000000000</precision_frequency>
    <duration_seconds>5</duration_seconds>
  </logentry>
  <logentry>
    <datetime>2026-01-01 00:00:10</datetime>
    <category>2</category>
    <dataset>1</dataset>
    <precision_start>n/a</precision_start>
    <precision_end>n/a</precision_end>
    <precision_frequency>n/a</precision_frequency>
    <duration_seconds>15000</duration_seconds>
  </logentry>
</Root>"""


class TestAdapterV1:
    """Tests for Machine/Run/Category XML adapter."""

    def _write_temp_xml(self, content):
        fd, path = tempfile.mkstemp(suffix=".xml")
        with os.fdopen(fd, "w") as f:
            f.write(content)
        return path

    def test_can_parse_valid(self):
        path = self._write_temp_xml(SAMPLE_V1_XML)
        try:
            adapter = AdapterV1()
            assert adapter.can_parse(path) is True
        finally:
            os.unlink(path)

    def test_can_parse_invalid(self):
        path = self._write_temp_xml(SAMPLE_V2_XML)
        try:
            adapter = AdapterV1()
            assert adapter.can_parse(path) is False
        finally:
            os.unlink(path)

    def test_parse_machine_info(self):
        path = self._write_temp_xml(SAMPLE_V1_XML)
        try:
            adapter = AdapterV1()
            result = adapter.parse(path)
            assert result is not None
            assert result.machine.name == "TestMachine"
            assert result.machine.cpu_name == "Test CPU"
            assert result.machine.cpu_max_clock_speed == 3000
            assert result.machine.cpu_is_hyper_threaded is True
        finally:
            os.unlink(path)

    def test_parse_run_scores(self):
        path = self._write_temp_xml(SAMPLE_V1_XML)
        try:
            adapter = AdapterV1()
            result = adapter.parse(path)
            assert len(result.runs) == 1
            run = result.runs[0]
            assert run.score1 == 50000.0
            assert run.score4 == 48000.0
            assert run.score16 == 45000.0
        finally:
            os.unlink(path)

    def test_parse_categories(self):
        path = self._write_temp_xml(SAMPLE_V1_XML)
        try:
            adapter = AdapterV1()
            result = adapter.parse(path)
            cats = result.runs[0].categories
            assert len(cats) == 1
            assert cats[0].name == "Memory test"
            assert cats[0].number == 1
            assert cats[0].avg_runtime == 5000.0
        finally:
            os.unlink(path)

    def test_parse_groups_and_tasks(self):
        path = self._write_temp_xml(SAMPLE_V1_XML)
        try:
            adapter = AdapterV1()
            result = adapter.parse(path)
            groups = result.runs[0].categories[0].groups
            assert len(groups) == 1
            assert groups[0].nr_of_threads == 1
            assert groups[0].group_score == 4500.0
            assert len(groups[0].tasks) == 1
            assert groups[0].tasks[0].duration_seconds == 4.5
        finally:
            os.unlink(path)


class TestAdapterV2:
    """Tests for log-entry XML adapter."""

    def _write_temp_xml(self, content):
        fd, path = tempfile.mkstemp(suffix=".xml")
        with os.fdopen(fd, "w") as f:
            f.write(content)
        return path

    def test_can_parse_valid(self):
        path = self._write_temp_xml(SAMPLE_V2_XML)
        try:
            adapter = AdapterV2()
            assert adapter.can_parse(path) is True
        finally:
            os.unlink(path)

    def test_parse_entries(self):
        path = self._write_temp_xml(SAMPLE_V2_XML)
        try:
            adapter = AdapterV2()
            entries = adapter.parse(path)
            assert entries is not None
            assert len(entries) == 2
            assert entries[0].category == 1
            assert entries[0].duration_seconds == 5.0
            assert entries[1].category == 2
            assert entries[1].duration_seconds == 15000.0
        finally:
            os.unlink(path)


class TestComputeDiff:
    """Tests for directionality-aware comparison math."""

    def test_lower_is_better_regression(self):
        # Duration increased = worse
        result = compute_diff(100.0, 120.0, "lower_is_better")
        assert result["diff"] == 20.0
        assert result["pct_change"] == 20.0
        assert result["assessment"] == "regression"

    def test_lower_is_better_improvement(self):
        # Duration decreased = better
        result = compute_diff(100.0, 80.0, "lower_is_better")
        assert result["diff"] == -20.0
        assert result["pct_change"] == -20.0
        assert result["assessment"] == "improvement"

    def test_higher_is_better_improvement(self):
        result = compute_diff(100.0, 120.0, "higher_is_better")
        assert result["assessment"] == "improvement"

    def test_higher_is_better_regression(self):
        result = compute_diff(100.0, 80.0, "higher_is_better")
        assert result["assessment"] == "regression"

    def test_unchanged(self):
        result = compute_diff(100.0, 100.0, "lower_is_better")
        assert result["assessment"] == "unchanged"
        assert result["diff"] == 0.0

    def test_none_values(self):
        result = compute_diff(None, 100.0)
        assert result["diff"] is None
        assert result["assessment"] == "N/A"

    def test_zero_baseline(self):
        result = compute_diff(0.0, 100.0)
        assert result["pct_change"] == float("inf")


class TestStabilityStats:
    """Tests for stability statistics computation."""

    def test_basic_stats(self):
        values = [10, 20, 30, 40, 50]
        stats = compute_stability_stats(values)
        assert stats["count"] == 5
        assert stats["mean"] == 30.0
        assert stats["median"] == 30.0
        assert stats["min"] == 10.0
        assert stats["max"] == 50.0

    def test_single_value(self):
        stats = compute_stability_stats([42.0])
        assert stats["count"] == 1
        assert stats["mean"] == 42.0
        assert stats["stdev"] == 0.0

    def test_empty_list(self):
        stats = compute_stability_stats([])
        assert stats["count"] is None

    def test_cv_calculation(self):
        values = [100, 100, 100, 100]
        stats = compute_stability_stats(values)
        assert stats["cv"] == 0.0


class TestOutlierDetection:
    """Tests for outlier detection."""

    def test_no_outliers(self):
        values = [10, 11, 12, 13, 14, 15]
        outliers = detect_outliers(values)
        assert len(outliers) == 0

    def test_detect_high_outlier(self):
        values = [10, 11, 12, 13, 14, 100]
        outliers = detect_outliers(values)
        assert len(outliers) >= 1
        assert any(o["value"] == 100.0 for o in outliers)

    def test_too_few_values(self):
        values = [1, 2, 3]
        outliers = detect_outliers(values)
        assert len(outliers) == 0


class TestDirectionality:
    """Tests for directionality rules."""

    def test_score_lower_is_better(self):
        assert get_directionality("score1") == "lower_is_better"
        assert get_directionality("score4") == "lower_is_better"
        assert get_directionality("score16") == "lower_is_better"

    def test_runtime_lower_is_better(self):
        assert get_directionality("avg_runtime") == "lower_is_better"
        assert get_directionality("group_score") == "lower_is_better"

    def test_override(self):
        overrides = {"custom_metric": "higher_is_better"}
        assert get_directionality("custom_metric", overrides) == "higher_is_better"

    def test_default(self):
        assert get_directionality("unknown_metric") == "lower_is_better"
