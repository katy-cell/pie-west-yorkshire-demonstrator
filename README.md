# PIE | West Yorkshire Connected Care

A HTL-branded Streamlit demonstrator for showing PIE as a **care-state, orchestration, predictive analytics and action-intelligence layer** across West Yorkshire.

This is not a shared-care-record replacement, a device platform or a static reporting dashboard. It demonstrates how PIE can connect evidence, pathway state, explanation and next action.

## What the current build shows

- **PIE command centre**: the West Yorkshire population baseline, 7/14/30-day modelled demand and a source-to-action operating flow.
- **Predict and act**: opaque PIE work items, visible care state, explainable pathway signals and recommended next actions.
- **Intervention studio**: scenario modelling for accepted handovers, targeted monitoring, medicines reviews and TEC / home-first response.
- **Population and equity**: published place populations and median ages, with modelled opportunity rates rather than an artificially balanced sample.
- **Architecture and assurance**: the relationship between this Streamlit experience and the wider PIE architecture, including governed ingestion, FHIR, pseudonymisation, explainability, workflow and outcome learning.

## Evidence and modelling approach

### Published baseline in this release

The model includes a fixed, versioned 2024 population baseline for the five West Yorkshire places:

| Place | Published population | Median age |
|---|---:|---:|
| Bradford District and Craven | 563,605 | 36 |
| Calderdale | 210,929 | 42 |
| Kirklees | 447,847 | 39 |
| Leeds | 845,189 | 36 |
| Wakefield | 367,666 | 40 |

The baseline is used to weight the regional model. Modelled opportunity rates also incorporate transparent median-age adjustments so that place patterns are not uniform.

### What is modelled

The 7/14/30-day care-opportunity forecasts, work items, operational states and intervention results are **modelled**. They are designed to represent what a connected PIE deployment could surface from a real population once authorised source data and local workflow signals are available. They are not claims about a current live caseload, patient count, incident count or service performance.

### Evidence framework

The app’s evidence catalogue references ONS local statistics, West Yorkshire population-health-management context, OHID Fingertips, NHSBSA polypharmacy comparators, NICE and NHS England pathway guidance, plus a future configurable layer for West Yorkshire APC, local formularies and local pathway standards.

## Architecture position

The Streamlit app is the **presentation and simulation layer** only. The wider PIE architecture is designed around:

1. Authorised data sources and ingestion
2. Pseudonymisation, FHIR normalisation, terminology and provenance
3. Care-state intelligence, explainable prediction and cohort analytics
4. Workflow orchestration, alerts, partner outputs and action routing
5. Outcome learning, fairness monitoring and model assurance

It is not currently connected to NHS FDP, a shared-care record, HAPI FHIR, AWS, a clinical system or any live source.

## Identity model

No names, NHS numbers, dates of birth, postcodes or direct identifiers are used. The demonstrator displays opaque PIE work-item keys only. In an authorised deployment, a tenant-held pseudonymisation service would create a stable key from an NHS number and keep re-identification information separate from the presentation and analytics layer.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

Open `http://localhost:8501`.

## Streamlit Community Cloud

```text
Branch: streamlit-demo
Main file path: app.py
```

## Repository map

```text
app.py                  Streamlit presentation layer
pie_model.py            Versioned public-baseline and modelled-opportunity engine
assets/branding/        PIE visual tokens and supplied logo asset
data/reference/         Existing evidence catalogues and public-source register
docs/                   Operating-model, methodology, governance and AI notes
public-data/            Controlled landing area for dated public extracts
tests/                  Model-validation tests
```

## Safety boundary

Do not add live credentials, NHS numbers, patient-level data, screenshots of live systems, API keys or unapproved local documentation. Any production pathway thresholds, formulary rules, referral criteria or escalation rules must be version-controlled and confirmed with the relevant clinical and operational owners.
