from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # to write into a file instead of rendering a window
import matplotlib.pyplot as plt

from src.utils.Utils import fmt_ts

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PLOTS_DIR = PROJECT_ROOT / "results" / "plots"


class AmmeterPlotter:

    def __init__(self, show: bool = False):
        self._show = show
        PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    def plot_time_series(self, measurements: list, title: str, session: str) -> Path:
        fig, ax = plt.subplots()
        ax.plot(range(1, len(measurements) + 1), measurements, marker='o')
        ax.set_title(title)
        ax.set_xlabel("Sample #")
        ax.set_ylabel("Current (A)")
        ax.grid(True)
        return self._save(fig, f"{session}_{title}_time_series")

    def plot_histogram(self, measurements: list, title: str, session: str) -> Path:
        fig, ax = plt.subplots()
        ax.hist(measurements, bins='auto', edgecolor='black')
        ax.set_title(title)
        ax.set_xlabel("Current (A)")
        ax.set_ylabel("Frequency")
        ax.grid(True, axis='y')
        return self._save(fig, f"{session}_{title}_histogram")

    def plot_comparison(self, results: list) -> Path:
        labels = [r['ammeter_type'] for r in results]
        data = [r['measurements'] for r in results]
        session = fmt_ts(results[0]['timestamp'])

        fig, ax = plt.subplots()
        ax.boxplot(data, labels=labels)
        ax.set_title("Current Distribution by Ammeter")
        ax.set_ylabel("Current (A)")
        ax.grid(True, axis='y')
        return self._save(fig, f"{session}_comparison")

    def _save(self, fig: plt.Figure, name: str) -> Path:
        path = PLOTS_DIR / f"{name}.png"
        fig.tight_layout()
        fig.savefig(path, dpi=150)
        if self._show:
            plt.show()
        plt.close(fig)
        return path
