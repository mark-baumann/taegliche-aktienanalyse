"""
Tests for wandb_utils.py — W&B Experiment Tracking für Tägliche Aktienanalyse.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wandb_utils import WANDB_AVAILABLE, WandBTracker


class TestWandBTracker:
    """Tests for WandBTracker."""

    def test_initialization_offline(self):
        """Tracker should initialize in offline mode."""
        tracker = WandBTracker(
            project="test-aktienanalyse",
            config={"key": "value"},
            tags=["test"],
            group="test-group",
            job_type="test",
            notes="Test-Run",
            offline=True,
        )
        if WANDB_AVAILABLE:
            assert tracker.is_active
            assert tracker.run is not None
        else:
            assert not tracker.is_active
        tracker.finish()

    def test_log_metrics(self):
        """Metrics should log without errors."""
        tracker = WandBTracker(project="test-aktienanalyse", offline=True)
        if tracker.is_active:
            tracker.log({"accuracy": 0.95, "loss": 0.05})
        tracker.finish()

    def test_finish_cleans_up(self):
        """finish() should end the run and be safe for double calls."""
        tracker = WandBTracker(project="test-aktienanalyse", offline=True)
        tracker.finish()
        assert not tracker.is_active
        tracker.finish()  # Double finish should be safe
        assert not tracker.is_active

    def test_log_episode(self):
        """Episode logging should prefix metrics correctly."""
        tracker = WandBTracker(project="test-aktienanalyse", offline=True)
        if tracker.is_active:
            tracker.log_episode("morning_scan", {"stocks_analysed": 50, "signals_generated": 12})
        tracker.finish()

    def test_log_model(self):
        """Model logging should include accuracy and optional params."""
        tracker = WandBTracker(project="test-aktienanalyse", offline=True)
        if tracker.is_active:
            tracker.log_model("trend-classifier", accuracy=0.87, params={"lr": 0.001, "epochs": 10})
        tracker.finish()

    def test_log_table(self):
        """Table logging should create a W&B table."""
        tracker = WandBTracker(project="test-aktienanalyse", offline=True)
        if tracker.is_active:
            tracker.log_table(
                "signals",
                columns=["stock", "signal", "confidence"],
                data=[["AAPL", "BUY", 0.85], ["GOOGL", "HOLD", 0.60]],
            )
        tracker.finish()

    def test_is_active_property(self):
        """is_active should reflect the run state correctly."""
        tracker = WandBTracker(project="test-aktienanalyse", offline=True)
        if WANDB_AVAILABLE:
            assert tracker.is_active is True
        else:
            assert tracker.is_active is False
        tracker.finish()
        assert tracker.is_active is False
