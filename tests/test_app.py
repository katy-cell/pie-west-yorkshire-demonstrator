from pathlib import Path
import subprocess
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_generator_creates_opaque_regional_synthetic_data() -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts" / "generate_synthetic_data.py")], check=True, cwd=str(ROOT))
    people = pd.read_csv(ROOT / "data" / "synthetic" / "synthetic_population.csv")
    events = pd.read_csv(ROOT / "data" / "synthetic" / "synthetic_events.csv")

    assert len(people) == 1200
    assert len(events) > len(people) * 3
    assert set(people["place"]) == {
        "Bradford District and Craven",
        "Calderdale",
        "Kirklees",
        "Leeds",
        "Wakefield",
    }
    assert people["person_key"].str.startswith("PIE-").all()
    assert not people["person_key"].str.contains("Margaret|Joseph|Aisha", case=False, regex=True).any()
    assert people["record_status"].eq("Synthetic demonstrator record").all()
    assert people["review_opportunity_30d_pct"].between(0, 100).all()
