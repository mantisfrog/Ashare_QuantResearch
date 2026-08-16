from __future__ import annotations

import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

import pyarrow.parquet as pq

from scripts.export_quant_snapshot import (
    MARKET_SCHEMA,
    METRIC_CODES,
    METRIC_ROWS,
    date_id,
    id_date,
    parse_iso_date,
    validate_parquet,
    write_table,
)


class ExportContractTests(unittest.TestCase):
    def test_metric_whitelist_is_fixed_and_unique(self) -> None:
        self.assertEqual(len(METRIC_CODES), 67)
        self.assertEqual(len(set(METRIC_CODES)), 67)
        self.assertEqual({row[4] for row in METRIC_ROWS}, {"元", "万元"})

    def test_date_id_round_trip(self) -> None:
        value = parse_iso_date("2026-08-07")
        self.assertEqual(date_id(value), 20260807)
        self.assertEqual(id_date(20260807), value)

    def test_market_schema_writes_decimal_values(self) -> None:
        row = (
            20260807, date(2026, 8, 7), "600000.SH",
            Decimal("10.12"), Decimal("10.30"), Decimal("10.05"), Decimal("10.26"),
            Decimal("3.456789012345"), Decimal("34.98469160"),
            Decimal("35.60692683"), Decimal("34.74272958"), Decimal("35.46865627"),
            123456789, Decimal("126543.2100"), 1000000000, 800000000,
            Decimal("1026000.0000"), Decimal("820800.0000"),
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "market.parquet"
            count = write_table(path, MARKET_SCHEMA, [row])
            validate_parquet(path, MARKET_SCHEMA, count)
            result = pq.read_table(path).to_pylist()[0]
        self.assertEqual(result["adj_close"], Decimal("35.46865627"))
        self.assertEqual(result["vol"], 123456789)


if __name__ == "__main__":
    unittest.main()