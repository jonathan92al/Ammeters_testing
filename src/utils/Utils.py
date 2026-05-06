import random


def generate_random_float(min_value: float, max_value: float) -> float:
    return random.uniform(min_value, max_value)


def fmt_ts(iso_ts: str) -> str:
    """Convert ISO timestamp to filename-safe format: '2026-05-06T14:23:01' -> '20260506_142301'"""
    return iso_ts.replace('-', '').replace('T', '_').replace(':', '')
