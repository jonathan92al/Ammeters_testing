import threading
import time

from Ammeters.Circutor_Ammeter import CircutorAmmeter
from Ammeters.Entes_Ammeter import EntesAmmeter
from Ammeters.Greenlee_Ammeter import GreenleeAmmeter
from src.testing.test_framework import AmmeterTestFramework
from src.utils.Utils import fmt_ts
from src.visualization.plotter import AmmeterPlotter


def run_greenlee_emulator():
    greenlee = GreenleeAmmeter(5001)
    greenlee.start_server()


def run_entes_emulator():
    entes = EntesAmmeter(5002)
    entes.start_server()


def run_circutor_emulator():
    circutor = CircutorAmmeter(5003)
    circutor.start_server()


if __name__ == "__main__":
    threading.Thread(target=run_greenlee_emulator, daemon=True).start()
    threading.Thread(target=run_entes_emulator, daemon=True).start()
    threading.Thread(target=run_circutor_emulator, daemon=True).start()

    # create an instance of the testing framework
    framework = AmmeterTestFramework()

    print("Test configuration:")
    for ammeter_type in framework.config['ammeters']:
        info = framework.get_test_info(ammeter_type)
        print(f"{info['ammeter_type']}: port {info['port']}, {info['measurements_count']} samples, {info['interval_seconds']:.1f}s interval")

    # Wait for the servers to start. Increase sleep time if you get connection errors on restart.
    time.sleep(2)

    results = framework.run_all_tests()

    print("\nResults:")
    for r in results:
        s = r['stats']
        print(f"{r['ammeter_type']}: mean={s['mean']:.4f}A  std={s['std_dev']:.4f}  min={s['min']:.4f}  max={s['max']:.4f}  ({r['actual_measurements']} samples, {r['duration_seconds']}s)")

    comparison = AmmeterTestFramework.compare_accuracy(results)
    print("\nAccuracy ranking (lower CV = more consistent):")
    for rank, (name, cv) in enumerate(comparison['ranking'], 1):
        print(f"  {rank}. {name}: CV={cv:.4f}")
    print(f"  Most consistent: {comparison['most_consistent']}")

    plotter = AmmeterPlotter()
    for r in results:
        plotter.plot_time_series(r['measurements'], r['ammeter_type'], fmt_ts(r['timestamp']))
        plotter.plot_histogram(r['measurements'], r['ammeter_type'], fmt_ts(r['timestamp']))
    path = plotter.plot_comparison(results)
    print(f"\nPlots saved to: {path.parent}")
