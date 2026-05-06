# Ammeter Testing Framework

A testing framework for three ammeter emulators: Greenlee, ENTES, and CIRCUTOR.

## Project Structure

```
Ammeters/
  base_ammeter.py        Base class for all ammeter emulators
  Greenlee_Ammeter.py    Greenlee emulator (Ohm's Law)
  Entes_Ammeter.py       ENTES emulator (Hall Effect)
  Circutor_Ammeter.py    CIRCUTOR emulator (Rogowski Coil)
  client.py              Socket client to request measurements
config/
  config.yaml            Sampling, analysis, and error simulation settings
src/
  testing/
    test_framework.py    Main test framework class
  results/
    result_manager.py    Save, load, filter, and compare results
  visualization/
    plotter.py           Time series, histogram, and comparison plots
  utils/
    config.py            YAML config loader
    logger.py            File + console logging setup
    Utils.py             generate_random_float helper
docs/
  design_decisions.md    Key design choices explained
main.py                  Entry point — starts emulators, runs full test suite, saves results and plots
```

## Setup

```bash
pip install -r requirements.txt
```

## Running

```bash
python main.py
```

## Output

| Location | Contents |
|---|---|
| `results/data/<timestamp>_<ammeter>.json` | One JSON file per test run |
| `results/plots/<timestamp>_<ammeter>_*.png` | Time series, histogram, and comparison box plot |
| `results/logs/<timestamp>.log` | Log file for each session |

## Configuration

Edit `config/config.yaml` to change sampling behaviour:

```yaml
testing:
  sampling:
    measurements_count: 10        # number of samples per ammeter
    total_duration_seconds: 10    # hard time limit per test
    sampling_frequency_hz: 1.0    # pause between samples (1/hz seconds)
```

### Error simulation

To test how the framework handles bad data, enable error simulation in `config/config.yaml`:

```yaml
error_simulation:
  enabled: true
  drop_rate: 0.1        # probability of a measurement returning None
  outlier_rate: 0.1     # probability of a wildly wrong value
  outlier_factor: 10.0  # multiplier applied to produce the outlier
  exception_rate: 0.05  # probability of a simulated connection error
```

All simulated errors are recorded in `result['errors']` and visible in the saved JSON.

## Ammeter emulators

| Ammeter | Port | Command | Method |
|---|---|---|---|
| Greenlee | 5001 | `MEASURE_GREENLEE -get_measurement` | Ohm's Law: I = V / R |
| ENTES | 5002 | `MEASURE_ENTES -get_data` | Hall Effect: I = B x K |
| CIRCUTOR | 5003 | `MEASURE_CIRCUTOR -get_measurement -current` | Rogowski Coil: I = integral(V dt) |

## Documentation

- `docs/design_decisions.md` — explains the key design choices behind the framework

## Bug fixes applied

- `main.py`: request calls were commented out — uncommented and added result printing.
- `src/testing/test_framework.py`: YAML command strings were passed as `str` to the socket client which expects `bytes` — fixed with `.encode('utf-8')`.
- `src/utils/logger.py`: logger had no handlers attached — added `FileHandler` and `StreamHandler`.
- `config/config.yaml`: `analysis` and `result_management` sections were empty — filled in with valid values.
- `Ammeters/Greenlee_Ammeter.py`: print statement used the `Ω` symbol which Windows console (cp1255 encoding) cannot render, causing the emulator to crash on first connection — replaced with `Ohm`.
