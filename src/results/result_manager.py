import json
from pathlib import Path
from src.utils.Utils import fmt_ts

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "results" / "data"


class ResultManager:
    def save(self, result: dict) -> Path:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        name = f"{fmt_ts(result['timestamp'])}_{result['ammeter_type']}"
        file_path = OUTPUT_DIR / f"{name}.json"
        serializable = {**result, 'id': str(result['id'])}
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(serializable, f, indent=2)
        return file_path

    def load(self, name: str) -> dict:
        file_path = OUTPUT_DIR / f"{name}.json"
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_results(self) -> list:
        if not OUTPUT_DIR.exists():
            return []
        results = []
        for file in sorted(OUTPUT_DIR.glob("*.json")):
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            results.append({
                'name': file.stem,
                'ammeter_type': data['ammeter_type'],
                'timestamp': data['timestamp'],
                'mean': data['stats']['mean'],
                'std_dev': data['stats']['std_dev'],
            })
        return results

    def filter_by(self, ammeter_type: str = None) -> list:
        results = self.list_results()
        if ammeter_type:
            results = [r for r in results if r['ammeter_type'] == ammeter_type]
        return sorted(results, key=lambda r: r['timestamp'])

    def compare(self, names: list) -> list:
        rows = []
        for name in names:
            data = self.load(name)
            rows.append({
                'name': name,
                'ammeter_type': data['ammeter_type'],
                'timestamp': data['timestamp'],
                'samples': data['actual_measurements'],
                **data['stats'],
            })
        return rows
