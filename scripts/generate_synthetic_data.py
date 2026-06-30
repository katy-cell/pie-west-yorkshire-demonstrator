from __future__ import annotations

"""Generate an evidence-grounded synthetic cohort for the PIE demonstrator.

This creates wholly fictional, opaque person keys. The *shape* of the cohort is
configured around West Yorkshire place weights and evidence tags. It deliberately
separates public population / guideline evidence from synthetic operational events.
"""

from pathlib import Path
from datetime import datetime, timedelta, timezone
import csv
import hashlib
import math
import random

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "synthetic"
REF = ROOT / "data" / "reference"
OUT.mkdir(parents=True, exist_ok=True)
REF.mkdir(parents=True, exist_ok=True)
RNG = random.Random(20260630)
NOW = datetime(2026, 6, 30, 9, 0, tzinfo=timezone.utc)

# A fixed implementation sample. Place allocations are proportional, not claims of live caseload.
# The source register records the official sources used to refresh these weights.
PLACES = {
    "Bradford District and Craven": {"n": 300, "code": "BDC", "areas": ["Bradford urban", "Keighley and Aire Valley", "Craven"], "imd_bias": [1, 1, 2, 2, 2, 3, 3, 4, 5]},
    "Calderdale": {"n": 105, "code": "CAL", "areas": ["Halifax", "Calder Valley", "Upper Valley"], "imd_bias": [1, 2, 3, 3, 4, 4, 5]},
    "Kirklees": {"n": 210, "code": "KIR", "areas": ["Dewsbury and Mirfield", "Huddersfield", "North Kirklees"], "imd_bias": [1, 2, 2, 3, 3, 4, 4, 5]},
    "Leeds": {"n": 410, "code": "LEE", "areas": ["East Leeds", "Inner Leeds", "North Leeds", "South Leeds", "West Leeds"], "imd_bias": [1, 2, 2, 3, 3, 4, 4, 5]},
    "Wakefield": {"n": 175, "code": "WAK", "areas": ["Five Towns", "Wakefield urban", "South East Wakefield"], "imd_bias": [1, 2, 2, 3, 4, 4, 5]},
}

PATHWAYS = [
    "Frailty, falls and TEC",
    "CVD remote monitoring",
    "Post-discharge coordination",
    "Medicines optimisation",
]

GUIDELINE_TAGS = {
    "Frailty, falls and TEC": "NICE NG249 · NHS England virtual wards framework",
    "CVD remote monitoring": "NICE NG136 / NG196 / NG106 · NHS England virtual wards framework",
    "Post-discharge coordination": "NHS England neighbourhood health guidance",
    "Medicines optimisation": "NICE condition-specific guidance · local formulary confirmation",
}


def opaque_person_key(place_code: str, index: int) -> str:
    """Opaque synthetic key. It is not derived from an NHS number."""
    digest = hashlib.sha256(f"pie-wy-demo-20260630-{place_code}-{index}".encode()).hexdigest()[:8].upper()
    return f"PIE-{place_code}-{digest}"


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def age_for_band(band: str) -> int:
    if band == "50–64":
        return RNG.randint(50, 64)
    if band == "65–74":
        return RNG.randint(65, 74)
    if band == "75–84":
        return RNG.randint(75, 84)
    return RNG.randint(85, 97)


def model_review_opportunity(
    *,
    age: int,
    pathway: str,
    imd: int,
    lives_alone: bool,
    unpaid_carer: bool,
    heart_failure: bool,
    atrial_fibrillation: bool,
    hypertension: bool,
    falls_history: bool,
    recent_discharge: bool,
    monitoring_change: bool,
    medicines_review_due: bool,
    ownership_gap: bool,
    delayed_source: bool,
) -> tuple[float, list[str], str]:
    """A demonstrator model: transparent, guideline-informed feature weighting.

    This is deliberately a review-opportunity model, not a clinical diagnosis,
    admission prediction or validated medical device.
    """
    logit = -2.15
    reasons: list[tuple[float, str]] = []

    def add(weight: float, reason: str, condition: bool) -> None:
        nonlocal logit
        if condition:
            logit += weight
            reasons.append((weight, reason))

    add(0.28, "age 85+", age >= 85)
    add(0.16, "age 75–84", 75 <= age < 85)
    add(0.42, "recent discharge", recent_discharge)
    add(0.58, "monitoring trend outside expected range", monitoring_change)
    add(0.46, "heart failure context", heart_failure)
    add(0.36, "atrial fibrillation review context", atrial_fibrillation)
    add(0.24, "hypertension review context", hypertension)
    add(0.33, "falls history context", falls_history)
    add(0.31, "medicines review due", medicines_review_due)
    add(0.37, "handover ownership unresolved", ownership_gap)
    add(0.22, "source data needs verification", delayed_source)
    add(0.12, "lives alone", lives_alone)
    add(0.07, "unpaid-carer context", unpaid_carer)
    add(0.10, "area deprivation context", imd <= 2)

    probability = round(100 * sigmoid(logit), 1)
    top_reasons = [reason for _, reason in sorted(reasons, reverse=True)[:3]]
    if pathway == "CVD remote monitoring":
        action = "Clinical review of monitoring, treatment and escalation plan"
    elif pathway == "Frailty, falls and TEC":
        action = "Coordinated falls / frailty review and TEC response check"
    elif pathway == "Post-discharge coordination":
        action = "Confirm ownership, follow-up and person communication"
    else:
        action = "Medicines optimisation review with local formulary context"
    return probability, top_reasons, action


def operational_score(ownership_gap: bool, due_status: str, source_freshness: str, person_informed: str) -> int:
    score = 8
    score += 42 if ownership_gap else 0
    score += {"Overdue": 28, "Due within 24 hours": 15, "On track": 2}[due_status]
    score += {"Delayed": 17, "Review required": 9, "Current": 0}[source_freshness]
    score += {"Pending": 12, "Sent": 0, "Not applicable": 0}[person_informed]
    return min(score, 100)


def priority_from_score(score: int, review_probability: float) -> str:
    combined = score * 0.65 + review_probability * 0.35
    if combined >= 66:
        return "Priority 1"
    if combined >= 47:
        return "Priority 2"
    if combined >= 30:
        return "Priority 3"
    return "Routine"


people: list[dict[str, object]] = []
events: list[dict[str, object]] = []
idx = 1
for place, cfg in PLACES.items():
    for local_idx in range(cfg["n"]):
        pathway = RNG.choices(PATHWAYS, [0.28, 0.30, 0.24, 0.18])[0]
        age_band = RNG.choices(["50–64", "65–74", "75–84", "85+"], [0.20, 0.29, 0.31, 0.20])[0]
        age = age_for_band(age_band)
        imd = RNG.choice(cfg["imd_bias"])
        lives_alone = RNG.random() < (0.22 if age < 65 else 0.34 if age < 75 else 0.44 if age < 85 else 0.53)
        unpaid_carer = RNG.random() < 0.19
        long_term_condition = RNG.random() < (0.40 if age < 65 else 0.58 if age < 75 else 0.72 if age < 85 else 0.82)
        heart_failure = pathway == "CVD remote monitoring" and RNG.random() < 0.27
        atrial_fibrillation = pathway == "CVD remote monitoring" and RNG.random() < 0.31
        hypertension = pathway == "CVD remote monitoring" and RNG.random() < 0.58
        falls_history = pathway == "Frailty, falls and TEC" and RNG.random() < 0.49
        recent_discharge = pathway == "Post-discharge coordination" or (pathway == "Frailty, falls and TEC" and RNG.random() < 0.20)
        monitoring_change = pathway == "CVD remote monitoring" and RNG.random() < 0.30
        medicines_review_due = pathway == "Medicines optimisation" or RNG.random() < 0.18
        ownership_gap = recent_discharge and RNG.random() < 0.31
        due_status = RNG.choices(["Overdue", "Due within 24 hours", "On track"], [0.12, 0.25, 0.63])[0]
        freshness = RNG.choices(["Current", "Review required", "Delayed"], [0.72, 0.20, 0.08])[0]
        person_informed = RNG.choices(["Sent", "Pending", "Not applicable"], [0.59, 0.29, 0.12])[0]
        review_probability, top_reasons, recommendation = model_review_opportunity(
            age=age, pathway=pathway, imd=imd, lives_alone=lives_alone, unpaid_carer=unpaid_carer,
            heart_failure=heart_failure, atrial_fibrillation=atrial_fibrillation, hypertension=hypertension,
            falls_history=falls_history, recent_discharge=recent_discharge, monitoring_change=monitoring_change,
            medicines_review_due=medicines_review_due, ownership_gap=ownership_gap, delayed_source=freshness != "Current",
        )
        op_score = operational_score(ownership_gap, due_status, freshness, person_informed)
        priority = priority_from_score(op_score, review_probability)
        state = "Awaiting handover acceptance" if ownership_gap else "Monitoring review due" if monitoring_change else "Scheduled review due" if medicines_review_due else "Coordinated pathway active"
        owner = "Receiving service not yet confirmed" if ownership_gap else RNG.choice(["Neighbourhood MDT", "Primary care team", "TEC Hub", "Virtual ward liaison", "Medicines optimisation team"])
        due = NOW + timedelta(hours=RNG.randint(-36, 168))
        key = opaque_person_key(cfg["code"], local_idx + 1)
        if key == opaque_person_key("LEE", 1):
            pathway = "Frailty, falls and TEC"; age = 86; age_band = "85+"; lives_alone = True; recent_discharge = True; falls_history = True
            ownership_gap = True; due_status = "Overdue"; freshness = "Review required"; person_informed = "Pending"
            review_probability, top_reasons, recommendation = model_review_opportunity(
                age=age, pathway=pathway, imd=1, lives_alone=lives_alone, unpaid_carer=unpaid_carer,
                heart_failure=False, atrial_fibrillation=False, hypertension=False, falls_history=falls_history,
                recent_discharge=recent_discharge, monitoring_change=False, medicines_review_due=False,
                ownership_gap=ownership_gap, delayed_source=True,
            )
            op_score = operational_score(ownership_gap, due_status, freshness, person_informed)
            priority = priority_from_score(op_score, review_probability)
            state = "Awaiting handover acceptance"; owner = "Receiving service not yet confirmed"; due = NOW - timedelta(hours=8)

        person = {
            "person_key": key,
            "place": place,
            "locality": RNG.choice(cfg["areas"]),
            "age_band": age_band,
            "age": age,
            "sex": RNG.choice(["Female", "Male", "Not recorded in synthetic model"]),
            "ethnicity_group": RNG.choice(["White", "Asian or Asian British", "Black, Black British, Caribbean or African", "Mixed or multiple ethnic groups", "Other ethnic group"]),
            "lives_alone": "Yes" if lives_alone else "No",
            "long_term_condition_context": "Yes" if long_term_condition else "No",
            "unpaid_carer_context": "Yes" if unpaid_carer else "No",
            "imd_quintile": imd,
            "digital_access_route": "Non-digital option required" if (age >= 85 and lives_alone) or (imd <= 2 and RNG.random() < 0.50) else RNG.choice(["Digital with support", "Digital likely suitable", "Needs preference check"]),
            "pathway": pathway,
            "current_state": state,
            "care_owner": owner,
            "next_action": recommendation,
            "next_action_due": due.isoformat(),
            "due_status": due_status,
            "source_freshness": freshness,
            "person_notification": person_informed,
            "operational_priority_score": op_score,
            "review_opportunity_30d_pct": review_probability,
            "priority_band": priority,
            "top_explainers": " | ".join(top_reasons),
            "evidence_tags": GUIDELINE_TAGS[pathway],
            "identity_design": "Opaque synthetic identifier; future production link through tenant-held pseudonymisation service",
            "record_status": "Synthetic demonstrator record",
        }
        people.append(person)

        base = NOW - timedelta(days=RNG.randint(1, 18))
        stages = [("Referral / pathway event received", "Authorised source system", "Event-led")]
        if recent_discharge:
            stages.append(("Discharge or transition recorded", "Acute care event feed", "Event-led"))
        stages.extend([
            ("Care-state normalised", "PIE care-state engine", "Near-real-time"),
            ("Action and owner evaluated", "PIE orchestration layer", "Near-real-time"),
        ])
        if not ownership_gap:
            stages.append(("Receiving service accepted responsibility", "Receiving service workflow", "Event-led"))
        if person_informed == "Sent":
            stages.append(("Person / carer communication recorded", "Communication service", "Scheduled"))
        for stage_idx, (event_type, source, mode) in enumerate(stages):
            event_time = base + timedelta(hours=stage_idx * RNG.randint(4, 13))
            events.append({
                "event_key": f"EV-{hashlib.sha1(f'{key}-{stage_idx}'.encode()).hexdigest()[:10].upper()}",
                "person_key": key,
                "event_time": event_time.isoformat(),
                "received_time": (event_time + timedelta(minutes=RNG.choice([2, 6, 12, 35, 90]))).isoformat(),
                "event_type": event_type,
                "source_category": source,
                "delivery_mode": mode,
                "confidence": RNG.choices(["High", "Medium", "Needs verification"], [0.64, 0.29, 0.07])[0],
                "record_status": "Synthetic demonstrator event",
            })
        idx += 1

with (OUT / "synthetic_population.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=people[0].keys())
    writer.writeheader(); writer.writerows(people)
with (OUT / "synthetic_events.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=events[0].keys())
    writer.writeheader(); writer.writerows(events)

context = [
    {"place": place, "synthetic_sample": cfg["n"], "population_weight": round(cfg["n"] / 1200, 4), "evidence_basis": "Place allocation weight derived from public population denominator refresh process", "context_status": "Public-source refresh controlled through calibration intake"}
    for place, cfg in PLACES.items()
]
with (OUT / "place_context.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=context[0].keys())
    writer.writeheader(); writer.writerows(context)

print(f"Generated {len(people)} opaque synthetic records and {len(events)} synthetic care events")
