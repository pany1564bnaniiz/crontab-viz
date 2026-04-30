# crontab-viz

> Parses crontab expressions and renders a human-readable schedule timeline in the terminal.

---

## Installation

```bash
pip install crontab-viz
```

Or install from source:

```bash
git clone https://github.com/yourname/crontab-viz.git
cd crontab-viz
pip install .
```

---

## Usage

Pass any valid crontab expression to visualize its schedule:

```bash
crontab-viz "*/15 9-17 * * 1-5"
```

**Example output:**

```
Expression : */15 9-17 * * 1-5
Description: Every 15 minutes, between 09:00–17:00, Monday through Friday

Next 5 occurrences:
  1. Mon 2024-06-10  09:00
  2. Mon 2024-06-10  09:15
  3. Mon 2024-06-10  09:30
  4. Mon 2024-06-10  09:45
  5. Mon 2024-06-10  10:00
```

You can also request more occurrences:

```bash
crontab-viz "0 8 * * *" --count 10
```

Or use it as a library:

```python
from crontab_viz import parse, render

schedule = parse("0 8 * * *")
render(schedule, count=5)
```

---

## Requirements

- Python 3.8+
- `croniter`
- `rich`

---

## License

This project is licensed under the [MIT License](LICENSE).