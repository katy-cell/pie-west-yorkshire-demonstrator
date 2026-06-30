# PIE | West Yorkshire Connected Care

A private, HTL-branded demonstrator for testing a person-led, cross-organisational care-intelligence model across West Yorkshire.

## What this version demonstrates

PIE is positioned as a **care-state, coordination, predictive analytics and exception-management layer**. It is not another dashboard, a shared-care-record replacement or a device platform.

The current Streamlit app includes:

- **Command centre**: pathway ownership, action clocks, source confidence and emerging demand.
- **Predict & prioritise**: guideline-informed review opportunities with explainable signals.
- **Intervention studio**: scenario modelling for handover acceptance, targeted monitoring and medicines-review capacity.
- **Population intelligence**: West Yorkshire place view with population, deprivation and access context.
- **Evidence & trust**: public-source catalogue, AI boundary and pseudonymisation design.

## Scope

- **Regional shell:** Bradford District and Craven, Calderdale, Kirklees, Leeds and Wakefield.
- **Detailed pathway lens:** Leeds frailty and technology-enabled care, with CVD/virtual ward logic retained because this was part of Stephen's original pathway discussion.
- **Identity model:** no first names, no direct identifiers and no NHS numbers in the interface. The app uses opaque PIE person keys.
- **Evidence model:** public data and national guidance calibrate the shape and review logic. Person-level pathway records remain synthetic unless and until an authorised pilot supplies real operational events.

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

Use:

```text
Branch: streamlit-demo
Main file path: app.py
```

## Repository map

```text
app.py                  Streamlit entry point
scripts/                Deterministic synthetic-data generator
assets/branding/        PIE visual tokens and supplied logo asset
data/reference/         Evidence catalogue for public data and guidance
data/synthetic/         Generated locally on first launch from a fixed seed
docs/                   Operating-model, methodology, governance and AI notes
public-data/            Controlled landing area for dated public extracts
tests/                  Baseline validation
```

## Brand

PIE visual tokens use the supplied logo artwork: deep PIE blue `#074695`, PIE blue `#0E74BA` and PIE magenta `#BE3F89`.

## Safety boundary

Do not add live NHS credentials, API keys, screenshots of live systems, patient-level data or unapproved local documentation. Local formularies, thresholds and pathway timing rules should be added only once they are source-controlled and confirmed with the relevant clinical or operational owner.
