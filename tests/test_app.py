from pathlib import Path
import subprocess
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_generator_creates_labelled_synthetic_data() -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts" / "generate_synthetic_data.py")], check=True, cwd=str(ROOT))
    people = pd.read_csv(ROOT / "data" / "synthetic" / "synthetic_population.csv")
    events = pd.read_csv(ROOT / "data" / "synthetic" / "synthetic_events.csv")
    assert len(people) == 1050
    assert len(events) == 4058
    assert people["data_classification"].eq("SYNTHETIC — NOT A REAL PERSON").all()
