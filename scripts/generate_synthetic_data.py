from __future__ import annotations
from pathlib import Path
from datetime import datetime, timedelta, timezone
import csv
import random

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "synthetic"
OUT.mkdir(parents=True, exist_ok=True)
RNG = random.Random(20260630)
NOW = datetime(2026, 6, 30, 9, 0, tzinfo=timezone.utc)

PLACES = {
    "Bradford District and Craven": {"n": 230, "areas": ["Bradford urban", "Keighley and Aire Valley", "Craven"], "imd": [1, 2, 2, 3, 3, 4, 5]},
    "Calderdale": {"n": 150, "areas": ["Calder Valley", "Halifax", "Upper Valley"], "imd": [1, 2, 3, 3, 4, 4, 5]},
    "Kirklees": {"n": 205, "areas": ["Dewsbury and Mirfield", "Huddersfield", "North Kirklees"], "imd": [1, 2, 2, 3, 4, 4, 5]},
    "Leeds": {"n": 290, "areas": ["Inner Leeds", "East Leeds", "North Leeds", "South Leeds", "West Leeds"], "imd": [1, 2, 2, 3, 3, 4, 5]},
    "Wakefield": {"n": 175, "areas": ["Wakefield urban", "Five Towns", "South East Wakefield"], "imd": [1, 2, 3, 3, 4, 4, 5]},
}

NAMES = ["Margaret", "Joseph", "Aisha", "David", "Rita", "Peter", "June", "William", "Sharon", "Ahmed", "Linda", "Michael", "Eileen", "Daniel", "Farah", "Susan"]
PATHWAYS = ["Post-discharge frailty", "Community frailty", "TEC and remote monitoring", "Medicines review", "Falls prevention"]
STATES = ["Awaiting handover acceptance", "Community action active", "Monitoring active", "Review due", "Pathway stable"]
OWNERS = ["Community frailty team", "Primary care team", "TEC hub", "Adult social care", "Virtual ward liaison"]
ACTIONS = {
    "Awaiting handover acceptance": "Receiving service to accept responsibility",
    "Community action active": "Complete agreed home or community contact",
    "Monitoring active": "Review remote-monitoring or telecare signal",
    "Review due": "Complete medicines or care-plan review",
    "Pathway stable": "Confirm next planned review and person communication",
}

rows: list[dict[str, object]] = []
events: list[dict[str, object]] = []
idx = 1
for place, cfg in PLACES.items():
    for _ in range(cfg["n"]):
        current_place = place
        age_band = RNG.choices(["65–74", "75–84", "85+"], [0.36, 0.39, 0.25])[0]
        age = RNG.randint(65, 74) if age_band == "65–74" else RNG.randint(75, 84) if age_band == "75–84" else RNG.randint(85, 96)
        living_alone = RNG.random() < (0.34 if age < 75 else 0.43 if age < 85 else 0.52)
        disability = RNG.random() < (0.23 if age < 75 else 0.36 if age < 85 else 0.49)
        unpaid_care = RNG.random() < 0.18
        deprivation = RNG.choice(cfg["imd"])
        digital = "May need non-digital route" if (age >= 85 and living_alone) or (deprivation <= 2 and RNG.random() < 0.55) else RNG.choice(["Digital route suitable with support", "Digital route likely suitable", "Needs assessment"])
        state = RNG.choices(STATES, [0.15, 0.29, 0.19, 0.22, 0.15])[0]
        pathway = RNG.choice(PATHWAYS)
        owner = "Unassigned" if state == "Awaiting handover acceptance" else RNG.choice(OWNERS)
        priority = "Critical" if state == "Awaiting handover acceptance" and RNG.random() < 0.35 else "High" if state in ["Awaiting handover acceptance", "Review due"] and RNG.random() < 0.58 else RNG.choice(["Medium", "Routine"])
        action_status = "Overdue" if priority == "Critical" else RNG.choice(["On track", "Due soon", "Overdue"])
        freshness = RNG.choices(["Current", "Review required", "Delayed"], [0.70, 0.21, 0.09])[0]
        person_id = f"PIE-WY-{idx:04d}"
        due = NOW + timedelta(hours=RNG.randint(-24, 120))
        if person_id == "PIE-WY-0001":
            current_place, state, owner, priority, action_status = "Leeds", "Awaiting handover acceptance", "Unassigned", "Critical", "Overdue"
            pathway, due, living_alone, age, age_band, freshness, digital = "Post-discharge frailty", NOW - timedelta(hours=8), True, 86, "85+", "Review required", "May need non-digital route"
        rows.append({
            "synthetic_person_id": person_id,
            "display_name": f"{NAMES[(idx - 1) % len(NAMES)]} · synthetic case",
            "place": current_place,
            "locality": RNG.choice(cfg["areas"]),
            "age_band": age_band,
            "age": age,
            "sex": RNG.choice(["Female", "Male", "Not stated in synthetic scenario"]),
            "ethnicity_group": RNG.choice(["White", "Asian or Asian British", "Black, Black British, Caribbean or African", "Mixed or multiple ethnic groups", "Other ethnic group"]),
            "living_arrangement": "Lives alone" if living_alone else "Lives with another adult",
            "disability_context": "Long-term condition / disability context" if disability else "No context modelled",
            "unpaid_carer_context": "Unpaid carer context" if unpaid_care else "No unpaid-carer context modelled",
            "imd_quintile": deprivation,
            "digital_access_context": digital,
            "pathway": pathway,
            "current_state": state,
            "care_owner": owner,
            "next_action": ACTIONS[state],
            "next_action_due": due.isoformat(),
            "action_status": action_status,
            "priority": priority,
            "data_freshness": freshness,
            "person_notification": RNG.choice(["Sent", "Pending", "Not applicable"]),
            "data_classification": "SYNTHETIC — NOT A REAL PERSON",
            "calibration_status": "Illustrative distribution — replace with dated public extracts",
        })
        base_time = NOW - timedelta(days=RNG.randint(1, 15))
        stages = [("Referral or discharge event received", "Acute / community source"), ("Care state normalised", "PIE synthetic engine"), ("Action assigned", "Synthetic pathway workflow")]
        if state != "Awaiting handover acceptance":
            stages.append(("Handover accepted", "Synthetic receiving service"))
        for stage_idx, (event_type, source) in enumerate(stages):
            event_time = base_time + timedelta(hours=stage_idx * 10)
            events.append({
                "event_id": f"EV-{idx:04d}-{stage_idx + 1}",
                "synthetic_person_id": person_id,
                "event_time": event_time.isoformat(),
                "received_time": (event_time + timedelta(minutes=RNG.choice([2, 8, 30, 120]))).isoformat(),
                "event_type": event_type,
                "source_system": source,
                "mode": RNG.choice(["Event-led", "Near-real-time", "Scheduled"]),
                "quality": RNG.choice(["Confirmed", "Validated", "Review required"]),
                "data_classification": "SYNTHETIC — NOT A REAL EVENT",
            })
        idx += 1

with (OUT / "synthetic_population.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
with (OUT / "synthetic_events.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=events[0].keys())
    writer.writeheader()
    writer.writerows(events)

contexts = [
    {"place": "Bradford District and Craven", "population_context": "Illustrative place context", "inequalities_signal": 4, "admissions_signal": 4, "medicines_signal": 3, "digital_access_signal": 3, "source_status": "Public-source calibration pending"},
    {"place": "Calderdale", "population_context": "Illustrative place context", "inequalities_signal": 3, "admissions_signal": 3, "medicines_signal": 3, "digital_access_signal": 3, "source_status": "Public-source calibration pending"},
    {"place": "Kirklees", "population_context": "Illustrative place context", "inequalities_signal": 4, "admissions_signal": 3, "medicines_signal": 4, "digital_access_signal": 3, "source_status": "Public-source calibration pending"},
    {"place": "Leeds", "population_context": "Illustrative place context", "inequalities_signal": 4, "admissions_signal": 4, "medicines_signal": 3, "digital_access_signal": 3, "source_status": "Public-source calibration pending"},
    {"place": "Wakefield", "population_context": "Illustrative place context", "inequalities_signal": 4, "admissions_signal": 4, "medicines_signal": 4, "digital_access_signal": 3, "source_status": "Public-source calibration pending"},
]
with (OUT / "place_context.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=contexts[0].keys())
    writer.writeheader()
    writer.writerows(contexts)

print(f"Generated {len(rows)} synthetic people and {len(events)} synthetic events")
