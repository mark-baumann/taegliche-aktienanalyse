"""
W&B Experiment Tracking für Tägliche Aktienanalyse
====================================================
Integriert Weights & Biases in die tägliche Aktienanalyse.
Loggt Episoden, Modell-Performance und Tabellen-Daten.

Usage:
    from wandb_utils import WandBTracker
    tracker = WandBTracker(project="taegliche-aktienanalyse", config={...})
    tracker.log_episode("analyse", {"stocks_analysed": 50})
    tracker.log_model("trend-classifier", accuracy=0.87, params={"lr": 0.001})
    tracker.log_table("signals", columns=["stock", "signal"], data=[["AAPL", "BUY"]])
    tracker.finish()
"""

import os
import time
from typing import Any, Optional

try:
    import wandb

    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False


class WandBTracker:
    """
    Encapsulated W&B tracker für die tägliche Aktienanalyse.

    Features:
    - Automatic offline mode when no API key
    - Git commit logging in online mode
    - Episoden-Logging (log_episode)
    - Modell-Performance-Logging (log_model)
    - Tabellen-Daten-Logging (log_table)
    """

    def __init__(
        self,
        project: str = "taegliche-aktienanalyse",
        config: Optional[dict] = None,
        tags: Optional[list] = None,
        group: Optional[str] = None,
        job_type: str = "analysis",
        notes: Optional[str] = None,
        offline: bool = False,
    ):
        self.project = project
        self.run = None
        self._start_time = time.time()

        if WANDB_AVAILABLE:
            try:
                mode = "offline" if offline or not os.environ.get("WANDB_API_KEY") else "online"
                self.run = wandb.init(
                    project=project,
                    config=config or {},
                    mode=mode,
                    tags=tags or ["aktienanalyse"],
                    group=group,
                    job_type=job_type,
                    notes=notes,
                    dir="wandb_runs",
                )
                if mode == "online":
                    try:
                        import subprocess

                        git_commit = subprocess.check_output(
                            ["git", "rev-parse", "--short", "HEAD"],
                            stderr=subprocess.DEVNULL,
                        ).decode().strip()
                        self.log({"git_commit": git_commit})
                    except Exception:
                        pass
                print(f"📊 W&B initialisiert (mode={mode}, project={project})")
            except Exception as e:
                print(f"⚠️  W&B-Init fehlgeschlagen: {e}")

    def log(self, metrics: dict, step: Optional[int] = None):
        """Log metrics to W&B."""
        if self.run:
            self.run.log(metrics, step=step)

    # ── Domain-specific log methods ──────────────────────────

    def log_episode(self, episode_name: str, metrics: dict, step: Optional[int] = None):
        """
        Loggt eine Analyse-Episode mit Metriken.

        Args:
            episode_name: Name der Episode (z.B. "morning_scan", "closing_analysis")
            metrics: Dict mit Metriken (z.B. {"stocks_analysed": 50, "signals_generated": 12})
        """
        prefixed = {f"episode/{episode_name}/{k}": v for k, v in metrics.items()}
        self.log(prefixed, step=step)

    def log_model(self, model_name: str, accuracy: float, params: Optional[dict] = None, step: Optional[int] = None):
        """
        Loggt Modell-Performance-Metriken.

        Args:
            model_name: Name des Modells (z.B. "trend-classifier", "signal-scorer")
            accuracy: Genauigkeit des Modells (0.0 - 1.0)
            params: Optionale Hyperparameter
        """
        metrics = {f"model/{model_name}/accuracy": accuracy}
        if params:
            for k, v in params.items():
                metrics[f"model/{model_name}/params/{k}"] = v
        self.log(metrics, step=step)

    def log_table(self, table_name: str, columns: list, data: list, step: Optional[int] = None):
        """
        Loggt tabellarische Daten als W&B-Tabelle.

        Args:
            table_name: Name der Tabelle (z.B. "signals", "portfolio")
            columns: Spaltennamen
            data: Zeilen als Liste von Listen
        """
        if self.run and WANDB_AVAILABLE:
            try:
                table = wandb.Table(columns=columns, data=data)
                self.log({f"table/{table_name}": table}, step=step)
            except Exception as e:
                print(f"⚠️  Tabellen-Logging fehlgeschlagen: {e}")

    def finish(self):
        """End the W&B run. Safe to call multiple times."""
        elapsed = time.time() - self._start_time
        if self.run:
            self.log({"total_time_seconds": elapsed})
            self.run.finish()
            self.run = None

    @property
    def is_active(self) -> bool:
        return self.run is not None
