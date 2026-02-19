"""Tests for locale-safe numeric parsing."""
import pytest
from qmeter_analyzer.utils.numeric import (
    parse_iso_duration,
    parse_number,
    safe_float,
    safe_int,
)


class TestParseIsoDuration:
    """Tests for ISO 8601 duration parsing."""

    def test_simple_seconds(self):
        assert parse_iso_duration("P0DT0H0M6.577S") == 6577.0

    def test_minutes_and_seconds(self):
        assert parse_iso_duration("P0DT0H1M30.5S") == 90500.0

    def test_hours(self):
        assert parse_iso_duration("P0DT1H0M0S") == 3600000.0

    def test_days(self):
        assert parse_iso_duration("P1DT0H0M0S") == 86400000.0

    def test_whole_seconds(self):
        assert parse_iso_duration("P0DT0H0M10.816S") == 10816.0

    def test_empty_string(self):
        assert parse_iso_duration("") is None

    def test_invalid_format(self):
        assert parse_iso_duration("not a duration") is None

    def test_zero_duration(self):
        assert parse_iso_duration("P0DT0H0M0S") == 0.0


class TestParseNumber:
    """Tests for locale-safe number parsing."""

    def test_simple_integer(self):
        val, warn = parse_number("5321")
        assert val == 5321.0
        assert warn is None

    def test_simple_decimal(self):
        val, warn = parse_number("153352.19")
        assert val == 153352.19
        assert warn is None

    def test_thousand_separator_comma(self):
        val, warn = parse_number("5,321")
        assert val == 5321.0

    def test_multiple_thousand_separators(self):
        val, warn = parse_number("1,234,567")
        assert val == 1234567.0
        assert warn is None

    def test_comma_and_dot(self):
        val, warn = parse_number("1,234.56")
        assert val == 1234.56
        assert warn is None

    def test_na_value(self):
        val, warn = parse_number("n/a")
        assert val is None
        assert warn is None

    def test_empty_string(self):
        val, warn = parse_number("")
        assert val is None

    def test_negative_number(self):
        val, warn = parse_number("-123.45")
        assert val == -123.45

    def test_large_number_with_commas(self):
        val, warn = parse_number("1,704")
        assert val == 1704.0


class TestSafeFloat:
    """Tests for safe_float helper."""

    def test_valid_number(self):
        assert safe_float("123.45") == 123.45

    def test_empty_returns_zero(self):
        assert safe_float("") == 0.0

    def test_na_returns_zero(self):
        assert safe_float("n/a") == 0.0


class TestSafeInt:
    """Tests for safe_int helper."""

    def test_valid_int(self):
        assert safe_int("42") == 42

    def test_empty_returns_default(self):
        assert safe_int("", 0) == 0

    def test_invalid_returns_default(self):
        assert safe_int("abc", 5) == 5

    def test_comma_separated(self):
        assert safe_int("1,000") == 1000
