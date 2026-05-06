from src.results.result_manager import ResultManager

# All greenlee runs, sorted by timestamp
runs = ResultManager.filter_by(ammeter_type='greenlee')
for run in runs:
  print(run['timestamp'], run['mean'])

# All runs across all ammeters
all_runs = ResultManager.filter_by()

# compare — put specific runs side by side:
# First grab the IDs you want (e.g. from filter_by)
runs = ResultManager.filter_by(ammeter_type='greenlee')
ids = [r['id'] for r in runs]

# Then compare them
rows = ResultManager.compare(ids)
for row in rows:
  print(f"{row['timestamp']}  mean={row['mean']:.4f}  std_dev={row['std_dev']:.4f}")

# Typical workflow — compare the last run of each ammeter type against each other:
latest = {}
for run in ResultManager.filter_by():
  latest[run['ammeter_type']] = run['id']  # overwrites, keeps most recent

rows = ResultManager.compare(list(latest.values()))
for row in rows:
  print(f"{row['ammeter_type']:<12} mean={row['mean']:.4f}  std_dev={row['std_dev']:.4f}")