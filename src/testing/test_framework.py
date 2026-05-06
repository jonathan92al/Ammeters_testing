import logging
import os
import random
import statistics
import time
from datetime import datetime
from uuid import uuid4
from Ammeters.client import request_current_from_ammeter
from src.results.result_manager import ResultManager
from src.utils.config import load_config

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger(__name__)


class AmmeterTestFramework:
    def __init__(self, config_path="config/config.yaml"):
        self.config = load_config(os.path.join(ROOT_DIR, '..', '..', config_path))
        self.results = ResultManager()

    def get_test_info(self, ammeter_type):
        ammeter = self.config['ammeters'][ammeter_type]
        sampling = self.config['testing']['sampling']
        return {
            'ammeter_type': ammeter_type,
            'port': ammeter['port'],
            'command': ammeter['command'].encode('utf-8'),
            'measurements_count': sampling['measurements_count'],
            'total_duration_seconds': sampling['total_duration_seconds'],
            'interval_seconds': 1 / sampling['sampling_frequency_hz'],
        }

    def run_test(self, ammeter_type):
        info = self.get_test_info(ammeter_type)
        measurements, errors = [], []
        start = time.time()
        deadline = start + info['total_duration_seconds']

        for i in range(info['measurements_count']):
            if time.time() >= deadline:
                logger.warning(f"{ammeter_type}: deadline reached after {i} samples")
                break
            wait = start + i * info['interval_seconds'] - time.time()
            if wait > 0:
                time.sleep(wait)
            try:
                data = request_current_from_ammeter(info['port'], info['command'])
                data = self._simulate_errors(data, i + 1, errors)
                if data is not None:
                    measurements.append(data)
            except Exception as e:
                errors.append(f"sample {i + 1}: {e}")
                logger.error(f"{ammeter_type} sample {i + 1} failed: {e}")

        result = {
            'id': uuid4(),
            'ammeter_type': ammeter_type,
            'timestamp': datetime.now().isoformat(timespec='seconds'),
            'duration_seconds': round(time.time() - start, 3),
            'requested_measurements': info['measurements_count'],
            'actual_measurements': len(measurements),
            'measurements': measurements,
            'stats': self._compute_stats(measurements),
            'errors': errors,
        }

        self.results.save(result)
        return result

    def run_all_tests(self):
        return [self.run_test(t) for t in self.config['ammeters']]

    def _simulate_errors(self, data, sample_num, errors):
        sim = self.config.get('error_simulation', {})
        if not sim.get('enabled'):
            return data
        if random.random() < sim.get('exception_rate', 0):
            raise ConnectionError(f"simulated connection error on sample {sample_num}")
        if random.random() < sim.get('drop_rate', 0):
            errors.append(f"sample {sample_num}: simulated drop")
            return None
        if data is not None and random.random() < sim.get('outlier_rate', 0):
            errors.append(f"sample {sample_num}: simulated outlier")
            return data * sim.get('outlier_factor', 10.0)
        return data

    @staticmethod
    def compare_accuracy(results):
        def cv(r):
            mean = r['stats']['mean']
            return r['stats']['std_dev'] / mean if mean else float('inf')
        ranking = sorted([(r['ammeter_type'], cv(r)) for r in results], key=lambda x: x[1])
        return {'ranking': ranking, 'most_consistent': ranking[0][0] if ranking else None}

    @staticmethod
    def _compute_stats(measurements):
        if not measurements:
            return {'mean': 0, 'median': 0, 'std_dev': 0, 'min': 0, 'max': 0}
        return {
            'mean': statistics.mean(measurements),
            'median': statistics.median(measurements),
            'std_dev': statistics.stdev(measurements) if len(measurements) > 1 else 0.0,
            'min': min(measurements),
            'max': max(measurements),
        }
