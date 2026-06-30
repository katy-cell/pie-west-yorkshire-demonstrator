# PIE | West Yorkshire Connected Care

A private, HTL-branded **synthetic demonstrator** for testing a person-led, cross-organisational care-coordination model across West Yorkshire.

> **Status:** Demonstrator and evidence framework. It contains no patient data, service-user data, live NHS data, credentials or live integrations. It is not a clinical decision-support system, a shared-care-record replacement or a production deployment.

## The proposition

The demonstrator does not assume that current records, telecare platforms, virtual wards or data assets are inadequate. It tests a more specific operating-model question:

> Can a trusted cross-organisational view show where a person is in a pathway, who has accepted responsibility, what needs to happen next, by when, how fresh the source information is and whether the person has been told?

PIE is modelled as a **potential care-state, coordination and exception-management layer** that could sit alongside authorised source systems and local services.

## Scope

- **Regional shell:** Bradford District and Craven, Calderdale, Kirklees, Leeds and Wakefield.
- **Detailed worked pathway:** Leeds frailty and technology-enabled care (TEC).
- **Data boundary:** public sources support future aggregate calibration. All present pathway states, people, events, clocks and local signals are synthetic.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

Open `http://localhost:8501`.

## Repository map

```text
app.py            Streamlit entry point
scripts/          Deterministic synthetic-data generator
assets/branding/  PIE visual tokens and supplied logo asset
public-data/      Controlled landing area for dated public extracts
data/synthetic/   Generated locally on first launch from a fixed seed
docs/             Operating-model, methodology, governance and source notes
tests/            Baseline validation
```

## Brand

PIE visual tokens use the supplied logo artwork: deep PIE blue `#074695`, PIE blue `#0E74BA` and PIE magenta `#BE3F89`. Check these against the final HTL brand book before external publication.

## GitHub and deployment

Keep the repository private. The synthetic cohort and events are regenerated deterministically from `scripts/generate_synthetic_data.py`. Do not add live NHS credentials, API keys, screenshots of live systems, patient-level data or unapproved local documentation. See `docs/governance.md` and `public-data/README.md`.
