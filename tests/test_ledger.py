"""Ledger tests: run files, schema, config hash, index regeneration."""

import json

import pytest

from trading_lab import ledger

from conftest import make_ohlcv


@pytest.fixture
def toy_ohlcv():
    return make_ohlcv([100 + i for i in range(120)])


class TestWriteRun:
    def test_run_and_record_writes_valid_file(self, toy_ohlcv, tmp_path):
        path = ledger.run_and_record(
            strategy="sma_crossover", instrument="TEST", timeframe="daily",
            ohlcv=toy_ohlcv, params={"fast": 10, "slow": 30},
            variants_tried=1, runs_dir=tmp_path)
        assert path.exists()
        assert path.parent == tmp_path
        rec = json.loads(path.read_text())
        for field in ledger.REQUIRED_FIELDS:
            assert field in rec, f"missing {field}"
        assert rec["strategy"] == "sma_crossover"
        assert rec["params"] == {"fast": 10, "slow": 30}
        assert rec["variants_tried"] == 1
        assert rec["run_id"] in path.name
        assert rec["config_hash"] in path.name
        # benchmark buy-and-hold metrics always present (founding-plan rail)
        assert rec["benchmark_metrics"]["total_return"] is not None
        assert rec["metrics"]["n_bars"] == 120
        # costs on by default
        assert rec["costs"] == {"slippage_bps": 5.0, "commission_bps": 1.0}
        assert "t+1 open" in rec["execution"]

    def test_missing_fields_rejected(self, tmp_path):
        with pytest.raises(ValueError, match="missing fields"):
            ledger.write_run({"strategy": "x"}, runs_dir=tmp_path)

    def test_config_hash_stable_and_sensitive(self):
        a = {"strategy": "sma", "params": {"fast": 10, "slow": 30}}
        b = {"params": {"slow": 30, "fast": 10}, "strategy": "sma"}
        c = {"strategy": "sma", "params": {"fast": 11, "slow": 30}}
        assert ledger.config_hash(a) == ledger.config_hash(b)  # order-free
        assert ledger.config_hash(a) != ledger.config_hash(c)

    def test_one_file_per_run_no_conflicts(self, toy_ohlcv, tmp_path):
        p1 = ledger.run_and_record(strategy="buy_and_hold", instrument="A",
                                   timeframe="daily", ohlcv=toy_ohlcv,
                                   runs_dir=tmp_path)
        p2 = ledger.run_and_record(strategy="buy_and_hold", instrument="A",
                                   timeframe="daily", ohlcv=toy_ohlcv,
                                   runs_dir=tmp_path)
        assert p1 != p2  # identical config, distinct run files


class TestIndex:
    def test_rebuild_index_from_run_files(self, toy_ohlcv, tmp_path):
        runs_dir = tmp_path / "runs"
        for instrument in ("AAA", "BBB"):
            ledger.run_and_record(strategy="buy_and_hold",
                                  instrument=instrument, timeframe="daily",
                                  ohlcv=toy_ohlcv, runs_dir=runs_dir)
        index = ledger.rebuild_index(experiments_dir=tmp_path)
        lines = [json.loads(l) for l in index.read_text().splitlines()]
        assert len(lines) == 2
        assert {l["instrument"] for l in lines} == {"AAA", "BBB"}
        for line in lines:
            assert (tmp_path / line["file"]).exists()
        # regeneration is idempotent
        assert ledger.rebuild_index(experiments_dir=tmp_path).read_text() == \
            index.read_text()
