"""Ledger tests: run files, schema, config hash, index regeneration,
holdout guard + committed-ledger audit."""

import json

import pandas as pd
import pytest

from trading_lab import config, ledger

from conftest import make_ohlcv


@pytest.fixture
def toy_ohlcv():
    return make_ohlcv([100 + i for i in range(120)])


@pytest.fixture
def holdout_spanning_ohlcv():
    """Toy series whose last bars land inside the locked holdout."""
    df = make_ohlcv([100 + i for i in range(60)], start="2024-11-01")
    assert df.index[-1] >= pd.Timestamp(config.HOLDOUT_START)
    return df


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


class TestHoldoutGuard:
    def test_record_with_holdout_data_rejected(self, holdout_spanning_ohlcv,
                                               tmp_path):
        with pytest.raises(ValueError, match="locked +holdout"):
            ledger.run_and_record(strategy="buy_and_hold", instrument="X",
                                  timeframe="daily",
                                  ohlcv=holdout_spanning_ohlcv,
                                  runs_dir=tmp_path)
        assert list(tmp_path.glob("*.json")) == []  # nothing written

    def test_write_run_is_a_choke_point(self, toy_ohlcv, tmp_path):
        """Hand-built records (bypassing build_record) are refused too."""
        path = ledger.run_and_record(strategy="buy_and_hold", instrument="X",
                                     timeframe="daily", ohlcv=toy_ohlcv,
                                     runs_dir=tmp_path)
        record = json.loads(path.read_text())
        record["data_end"] = str(pd.Timestamp(config.HOLDOUT_START))
        with pytest.raises(ValueError, match="locked +holdout"):
            ledger.write_run(record, runs_dir=tmp_path)

    def test_boundary_is_exclusive(self, tmp_path):
        """data_end strictly before HOLDOUT_START is fine."""
        last_ok = pd.Timestamp(config.HOLDOUT_START) - pd.Timedelta(days=1)
        df = make_ohlcv([100.0] * 30,
                        start=str(last_ok - pd.Timedelta(days=29)), freq="D")
        assert df.index[-1] == last_ok
        path = ledger.run_and_record(strategy="buy_and_hold", instrument="X",
                                     timeframe="daily", ohlcv=df,
                                     runs_dir=tmp_path)
        assert "holdout_unlocked" not in json.loads(path.read_text())

    def test_explicit_unlock_stamps_visible_marker(self, holdout_spanning_ohlcv,
                                                   tmp_path):
        runs_dir = tmp_path / "runs"
        path = ledger.run_and_record(strategy="buy_and_hold", instrument="X",
                                     timeframe="daily",
                                     ohlcv=holdout_spanning_ohlcv,
                                     runs_dir=runs_dir, holdout_unlocked=True)
        rec = json.loads(path.read_text())
        assert rec["holdout_unlocked"] is True
        # the marker survives index regeneration (rows self-declare)
        index = ledger.rebuild_index(experiments_dir=tmp_path)
        rows = [json.loads(l) for l in index.read_text().splitlines()]
        assert rows[0]["holdout_unlocked"] is True


class TestCommittedLedgerAudit:
    def test_every_committed_row_respects_holdout(self):
        """Audit the REAL ledger: no data_end >= HOLDOUT_START without the
        explicit 'holdout_unlocked' marker (compared as timestamps)."""
        holdout = pd.Timestamp(config.HOLDOUT_START)
        offenders = []

        index = config.EXPERIMENTS_DIR / "index.jsonl"
        assert index.exists(), "experiments/index.jsonl missing"
        for lineno, line in enumerate(index.read_text().splitlines(), 1):
            rec = json.loads(line)
            if pd.Timestamp(rec["data_end"]) >= holdout \
                    and not rec.get("holdout_unlocked"):
                offenders.append(f"index.jsonl:{lineno} run_id={rec['run_id']}")

        run_files = sorted(config.RUNS_DIR.glob("*.json"))
        assert run_files, "experiments/runs/ is empty"
        for path in run_files:
            rec = json.loads(path.read_text())
            if pd.Timestamp(rec["data_end"]) >= holdout \
                    and not rec.get("holdout_unlocked"):
                offenders.append(f"runs/{path.name}")

        assert not offenders, (
            "ledger rows reach into the locked holdout without the "
            f"'holdout_unlocked' marker: {offenders}")


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
