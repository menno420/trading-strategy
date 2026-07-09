"""Walk-forward tests: split boundaries and end-to-end run."""

import pandas as pd
import pytest

from trading_lab.strategies import sma_crossover
from trading_lab.walkforward import Split, generate_splits, walk_forward


class TestSplitBoundaries:
    def test_hand_computed_splits(self):
        # 100 bars, train 50, test 20, step defaults to test_size (20):
        # exactly two splits fit
        splits = generate_splits(100, train_size=50, test_size=20)
        assert splits == [
            Split(train_start=0, train_end=50, test_start=50, test_end=70),
            Split(train_start=20, train_end=70, test_start=70, test_end=90),
        ]

    def test_test_follows_train_no_overlap(self):
        for sp in generate_splits(500, 100, 30):
            assert sp.test_start == sp.train_end  # test is the NEXT window
            assert sp.test_end > sp.test_start
            assert sp.train_start >= 0

    def test_test_windows_contiguous_with_default_step(self):
        splits = generate_splits(400, 100, 50)
        for prev, nxt in zip(splits, splits[1:]):
            assert nxt.test_start == prev.test_end

    def test_never_exceeds_data(self):
        splits = generate_splits(137, 60, 25)
        assert all(sp.test_end <= 137 for sp in splits)

    def test_too_little_data_yields_no_splits(self):
        assert generate_splits(60, 50, 20) == []

    def test_bad_sizes_rejected(self):
        with pytest.raises(ValueError):
            generate_splits(100, 0, 20)
        with pytest.raises(ValueError):
            generate_splits(100, 50, 20, step=-1)


class TestWalkForward:
    def test_end_to_end(self, random_walk):
        grid = {"fast": [5, 10], "slow": [20, 40]}
        out = walk_forward(random_walk, sma_crossover.generate, grid,
                           train_size=120, test_size=40)
        n_splits = len(out["splits"])
        assert n_splits == len(generate_splits(len(random_walk), 120, 40))
        assert n_splits >= 2
        # stitched OOS returns cover exactly the test windows
        assert len(out["oos_returns"]) == n_splits * 40
        # chosen params always come from the grid (fast < slow enforced)
        for s in out["splits"]:
            assert s["params"]["fast"] in grid["fast"]
            assert s["params"]["slow"] in grid["slow"]
            assert s["params"]["fast"] < s["params"]["slow"]
        # multiple-testing discipline: grid size x splits
        assert out["variants_tried"] == 4 * n_splits
        # OOS equity is the compounded stitched returns
        assert out["oos_equity"].iloc[-1] == pytest.approx(
            (1 + out["oos_returns"]).prod())

    def test_explicit_variant_list_grid(self, random_walk):
        # Constraint-filtered grids are passed as an explicit list of param
        # dicts (e.g. fast < slow only); walk_forward must use them verbatim.
        variants = [{"fast": 5, "slow": 20}, {"fast": 10, "slow": 40}]
        out = walk_forward(random_walk, sma_crossover.generate, variants,
                           train_size=120, test_size=40)
        n_splits = len(out["splits"])
        assert out["variants_tried"] == len(variants) * n_splits
        for s in out["splits"]:
            assert s["params"] in variants

    def test_empty_grid_rejected(self, random_walk):
        with pytest.raises(ValueError, match="grid"):
            walk_forward(random_walk, sma_crossover.generate, {},
                         train_size=100, test_size=40)

    def test_insufficient_data_rejected(self, random_walk):
        with pytest.raises(ValueError, match="not enough bars"):
            walk_forward(random_walk.iloc[:50], sma_crossover.generate,
                         {"fast": [5], "slow": [20]},
                         train_size=100, test_size=40)
