from __future__ import annotations

"""In-memory model for the PIE West Yorkshire demonstrator.

The app intentionally uses a fixed, versioned public population baseline and
modelled care opportunities. It does not persist mock patient data or claim to
represent live operational events.
"""

from hashlib import sha256
from random import Random
from typing import Any

import pandas as pd

MODEL_VERSION = "WY-PIE-3.0"
RNG = Random(20260630)

# ONS mid-2024 local population estimates and ONS local-statistics median age.
# These values are deliberately versioned in code so the demonstrator remains
# reproducible until the next approved public-data refresh.
PLACE_BASELINE: list[dict[str, Any]] = [
    {"place": "Bradford District and Craven", "place_code": "BDC", "population": 563_605, "median_age": 36, "context": "Largest younger population profile in the five places"},
    {"place": "Calderdale", "place_code": "CAL", "population": 210_929, "median_age": 42, "context": "Oldest median-age profile in the five places"},
    {"place": "Kirklees", "place_code": "KIR", "population": 447_847, "median_age": 39, "context": "Above-system median age with diverse neighbourhood profiles"},
    {"place": "Leeds", "place_code": "LEE", "population": 845_189, "median_age": 36, "context": "Largest place population and detailed frailty / TEC pathway lens"},
    {"place": "Wakefield", "place_code": "WAK", "population": 367_666, "median_age": 40, "context": "Older-than-system median-age profile"},
]

# These are scenario rates for a 30-day planning horizon, not observed caseloads
# or clinical prevalence. The age adjustment uses the published median-age
# difference to avoid uniform place patterns.
PATHWAY_CONFIGURATION: list[dict[str, Any]] = [
    {
        "pathway": "Frailty, falls and TEC",
        "base_rate_per_10k": 17.5,
        "age_sensitivity": 1.45,
        "priority_share": 0.34,
        "evidence_basis": "NICE NG249 · NHS England frailty and virtual ward guidance",
        "next_action": "Co-ordinated frailty review, falls response and TEC / home-first check",
        "source_chain": "Primary care · community services · TEC / device status · SDoH context",
    },
    {
        "pathway": "CVD remote monitoring",
        "base_rate_per_10k": 12.0,
        "age_sensitivity": 1.15,
        "priority_share": 0.29,
        "evidence_basis": "NICE NG136 / NG196 / NG106 · West Yorkshire hypertension guidance",
        "next_action": "Clinical review of monitoring trend, treatment plan and escalation route",
        "source_chain": "Primary care · observation feed · prescribing context · community follow-up",
    },
    {
        "pathway": "Post-discharge coordination",
        "base_rate_per_10k": 11.0,
        "age_sensitivity": 0.55,
        "priority_share": 0.37,
        "evidence_basis": "NHS England neighbourhood health and virtual ward operating model",
        "next_action": "Confirm accountable owner, follow-up date and person / carer communication",
        "source_chain": "Acute discharge event · community service · primary care · social care status",
    },
    {
        "pathway": "Medicines optimisation",
        "base_rate_per_10k": 14.5,
        "age_sensitivity": 1.05,
        "priority_share": 0.27,
        "evidence_basis": "NICE NG5 / NG56 · NHSBSA polypharmacy comparators · local formulary layer",
        "next_action": "Structured medicines review with local formulary and shared decision context",
        "source_chain": "NHSBSA prescribing · primary care record · medicines review workflow",
    },
]


def _age_modifier(median_age: int, sensitivity: float) -> float:
    """Use published median-age variation as a transparent demand modifier."""
    return max(0.78, min(1.30, 1 + ((median_age - 38) / 38) * sensitivity))


def _opaque_key(place_code: str, pathway: str, index: int) -> str:
    digest = sha256(f"{MODEL_VERSION}|{place_code}|{pathway}|{index}".encode("utf-8")).hexdigest()[:9].upper()
    return f"PIE-{place_code}-{digest}"


def build_population_baseline() -> pd.DataFrame:
    baseline = pd.DataFrame(PLACE_BASELINE)
    baseline["population_share"] = baseline["population"] / baseline["population"].sum()
    baseline["published_baseline"] = "ONS mid-2024 population estimate and local-statistics median age"
    return baseline


def build_forecast() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for place in PLACE_BASELINE:
        for pathway in PATHWAY_CONFIGURATION:
            modifier = _age_modifier(place["median_age"], pathway["age_sensitivity"])
            expected_30d = int(round(place["population"] / 10_000 * pathway["base_rate_per_10k"] * modifier))
            priority_30d = int(round(expected_30d * pathway["priority_share"]))
            rows.append(
                {
                    "place": place["place"],
                    "place_code": place["place_code"],
                    "population": place["population"],
                    "median_age": place["median_age"],
                    "pathway": pathway["pathway"],
                    "expected_7d": max(1, int(round(expected_30d * 0.27))),
                    "expected_14d": max(1, int(round(expected_30d * 0.53))),
                    "expected_30d": max(1, expected_30d),
                    "priority_30d": max(1, priority_30d),
                    "opportunities_per_10k": round(expected_30d / place["population"] * 10_000, 1),
                    "age_modifier": round(modifier, 3),
                    "evidence_basis": pathway["evidence_basis"],
                    "recommended_next_action": pathway["next_action"],
                    "source_chain": pathway["source_chain"],
                    "provenance": "Published denominator + transparent scenario rate + age-profile adjustment",
                }
            )
    return pd.DataFrame(rows)


def _allocate_modelled_records(forecast: pd.DataFrame, target: int = 180) -> list[int]:
    weights = forecast["expected_30d"].tolist()
    total = sum(weights)
    raw = [weight / total * target for weight in weights]
    counts = [max(1, int(value)) for value in raw]
    remainder = target - sum(counts)
    ranked = sorted(range(len(raw)), key=lambda i: raw[i] - int(raw[i]), reverse=True)
    cursor = 0
    while remainder > 0:
        counts[ranked[cursor % len(ranked)]] += 1
        remainder -= 1
        cursor += 1
    while remainder < 0:
        candidates = [i for i, count in enumerate(counts) if count > 1]
        counts[candidates[cursor % len(candidates)]] -= 1
        remainder += 1
        cursor += 1
    return counts


def build_modelled_work_items(forecast: pd.DataFrame) -> pd.DataFrame:
    states = {
        "Frailty, falls and TEC": [
            "Risk pattern identified",
            "Assessment or TEC response to confirm",
            "Plan and accountable owner to confirm",
            "Active monitoring with review window",
        ],
        "CVD remote monitoring": [
            "Monitoring trend flagged for review",
            "Clinical plan review due",
            "Source observation requires confirmation",
            "Active monitoring with escalation route",
        ],
        "Post-discharge coordination": [
            "Discharge event received",
            "Receiving service acceptance pending",
            "Follow-up and person communication to confirm",
            "Co-ordinated transition active",
        ],
        "Medicines optimisation": [
            "Structured review opportunity identified",
            "Medicines reconciliation to confirm",
            "Shared decision / adherence conversation due",
            "Review plan active",
        ],
    }
    confidence = ["High", "Moderate", "Requires source confirmation"]
    windows = ["0–7 days", "8–14 days", "15–30 days"]
    rows: list[dict[str, Any]] = []
    allocations = _allocate_modelled_records(forecast)
    for allocation, (_, row) in zip(allocations, forecast.iterrows()):
        for index in range(allocation):
            state = states[row["pathway"]][index % len(states[row["pathway"]])]
            confidence_value = confidence[(index + len(row["place"])) % len(confidence)]
            priority = "Priority attention" if index < max(1, round(allocation * row["priority_30d"] / row["expected_30d"])) else "Planned review"
            score = min(99, int(46 + row["age_modifier"] * 18 + (17 if priority == "Priority attention" else 3) + (index % 9)))
            rows.append(
                {
                    "pie_work_item": _opaque_key(row["place_code"], row["pathway"], index),
                    "record_type": "Modelled operational record",
                    "place": row["place"],
                    "pathway": row["pathway"],
                    "attention_window": windows[index % len(windows)],
                    "priority": priority,
                    "care_state": state,
                    "source_chain": row["source_chain"],
                    "model_confidence": confidence_value,
                    "pie_attention_index": score,
                    "why_now": f"Published population baseline · {row['pathway']} review pattern · {state.lower()}",
                    "recommended_next_action": row["recommended_next_action"],
                    "evidence_basis": row["evidence_basis"],
                    "provenance": "Modelled exemplar. No direct identifier, NHS number or live operational event.",
                }
            )
    return pd.DataFrame(rows)


def build_architecture_layers() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "layer": "1. Source and ingestion",
                "production_capability": "EPR, primary care, community, prescribing, public SDoH, device and ambient inputs through approved adapters",
                "demonstrator_representation": "Versioned public West Yorkshire population baseline and modelled event patterns",
                "value": "Bring fragmented signals into one governed flow",
            },
            {
                "layer": "2. Trust, identity and interoperability",
                "production_capability": "Pseudonymisation, FHIR normalisation, terminology mapping, provenance and role-based access",
                "demonstrator_representation": "Opaque PIE work-item identifiers and visible source / evidence lineage",
                "value": "Make every signal traceable and safe to use",
            },
            {
                "layer": "3. Care-state and intelligence",
                "production_capability": "Care-state engine, feature store, predictive models, explainability and cohort analytics",
                "demonstrator_representation": "Modelled care opportunities, attention index, forecast horizons and explainers",
                "value": "Turn information into an understanding of what happens next",
            },
            {
                "layer": "4. Orchestration and action",
                "production_capability": "Workflow engine, alerts, APIs, task routing, partner-facing outputs and event-driven escalation",
                "demonstrator_representation": "Intervention scenarios and recommended next-action pathways",
                "value": "Move from insight to accountable co-ordination",
            },
            {
                "layer": "5. Learning and assurance",
                "production_capability": "Outcome monitoring, bias checks, feedback loops, audit trail and governed model lifecycle",
                "demonstrator_representation": "Evidence catalogue and transparent model assumptions",
                "value": "Prove value, improve safely and maintain trust",
            },
        ]
    )


def build_evidence_catalogue() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"source": "ONS local statistics", "use": "2024 place population denominator and median age", "type": "Published baseline", "status": "Versioned in this release"},
            {"source": "West Yorkshire ICB / PHM approach", "use": "Population segmentation, proactive care and inequality context", "type": "Operating-model context", "status": "Evidence framework"},
            {"source": "OHID Fingertips", "use": "Falls, readmission and population-outcomes benchmarking", "type": "Outcome benchmark", "status": "Reference layer"},
            {"source": "NHSBSA polypharmacy comparators", "use": "Medicines-review opportunity design", "type": "Medicines intelligence", "status": "Reference layer"},
            {"source": "NICE and NHS England guidance", "use": "Frailty, falls, CVD, medicines optimisation, virtual wards and neighbourhood health", "type": "Clinical / service logic", "status": "Evidence basis"},
            {"source": "West Yorkshire APC and local pathways", "use": "Future local formulary, thresholds and escalation rules", "type": "Configurable local layer", "status": "To be versioned with local owners"},
        ]
    )


def build_model() -> dict[str, pd.DataFrame]:
    population = build_population_baseline()
    forecast = build_forecast()
    work_items = build_modelled_work_items(forecast)
    architecture = build_architecture_layers()
    evidence = build_evidence_catalogue()
    return {
        "population": population,
        "forecast": forecast,
        "work_items": work_items,
        "architecture": architecture,
        "evidence": evidence,
    }
