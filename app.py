from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data" / "synthetic"
GENERATOR = ROOT / "scripts" / "generate_synthetic_data.py"
LOGO = ROOT / "assets" / "branding" / "pie_logo_mark_rgb.jpg"
EVIDENCE = ROOT / "data" / "reference" / "evidence_catalogue.csv"

PIE_DEEP = "#074695"
PIE_BLUE = "#0E74BA"
PIE_MAGENTA = "#BE3F89"
PIE_INK = "#0B2747"
PIE_SLATE = "#4E657D"
PIE_GREEN = "#177B63"
PIE_AMBER = "#A65D00"


def ensure_demo_data() -> None:
    required = [DATA_DIR / "synthetic_population.csv", DATA_DIR / "synthetic_events.csv", DATA_DIR / "place_context.csv"]
    if all(path.exists() for path in required):
        return
    subprocess.run([sys.executable, str(GENERATOR)], check=True, cwd=str(ROOT))


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ensure_demo_data()
    people = pd.read_csv(DATA_DIR / "synthetic_population.csv", parse_dates=["next_action_due"])
    events = pd.read_csv(DATA_DIR / "synthetic_events.csv", parse_dates=["event_time", "received_time"])
    context = pd.read_csv(DATA_DIR / "place_context.csv")
    evidence = pd.read_csv(EVIDENCE)
    return people, events, context, evidence


def apply_brand() -> None:
    st.markdown(f"""
    <style>
    .stApp {{ background: linear-gradient(180deg, #F7FAFE 0%, #FFFFFF 38%); }}
    .block-container {{ max-width: 1460px; padding-top: 1.2rem; padding-bottom: 1.2rem; }}
    [data-testid="stSidebar"] {{ background: #FFFFFF; border-right: 1px solid #DDE8F3; }}
    h1,h2,h3 {{ color: {PIE_INK}; letter-spacing: -.028em; }}
    .eyebrow {{ color: {PIE_MAGENTA}; font-weight: 800; text-transform: uppercase; letter-spacing: .13em; font-size: .73rem; }}
    .hero {{ border: 1px solid #D5E5F3; border-radius: 22px; padding: 1.35rem 1.5rem; margin-bottom: 1.2rem; background: radial-gradient(circle at 92% 10%, rgba(190,63,137,.12), transparent 24%), linear-gradient(120deg, #FFFFFF, #EDF6FD); }}
    .hero h1 {{ margin: .18rem 0 .45rem; font-size: clamp(2rem, 3vw, 3.15rem); }}
    .hero p {{ margin: 0; color: {PIE_SLATE}; font-size: 1.03rem; max-width: 980px; }}
    .metric-card {{ border: 1px solid #DDE8F5; border-radius: 15px; background: #FFFFFF; min-height: 108px; padding: .85rem .95rem; box-shadow: 0 8px 24px rgba(22,76,130,.045); }}
    .metric-label {{ color: {PIE_SLATE}; font-size: .75rem; font-weight: 750; }}
    .metric-value {{ color: {PIE_DEEP}; font-size: 1.72rem; font-weight: 820; line-height: 1.16; margin: .32rem 0 .16rem; }}
    .metric-sub {{ color: {PIE_SLATE}; font-size: .76rem; }}
    .callout {{ border-left: 4px solid {PIE_MAGENTA}; border-radius: 0 12px 12px 0; background: #FFF9FD; padding: .9rem 1rem; color: {PIE_INK}; }}
    .footer {{ margin-top: 2rem; padding-top: .75rem; border-top: 1px solid #E3EBF5; color: #6B7F95; font-size: .73rem; }}
    .small-tag {{ display:inline-block; border:1px solid #D8E6F2; border-radius:999px; background:#FFFFFF; padding:.22rem .55rem; color:{PIE_SLATE}; font-size:.72rem; margin:0 .35rem .35rem 0; }}
    </style>
    """, unsafe_allow_html=True)


def hero(title: str, subtitle: str) -> None:
    st.markdown(f"<div class='hero'><div class='eyebrow'>PIE | West Yorkshire Connected Care</div><h1>{title}</h1><p>{subtitle}</p></div>", unsafe_allow_html=True)


def metric(label: str, value: int | float | str, subtitle: str) -> None:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div><div class='metric-sub'>{subtitle}</div></div>", unsafe_allow_html=True)


def footer() -> None:
    st.markdown("<div class='footer'>PIE™ West Yorkshire Connected Care demonstrator · public evidence framework + synthetic person-level simulation · decision support with human review</div>", unsafe_allow_html=True)


def sidebar() -> str:
    with st.sidebar:
        if LOGO.exists(): st.image(str(LOGO), width=90)
        st.markdown("### PIE™")
        st.caption("Patient Insight Engine")
        st.divider()
        page = st.radio("Navigate", ["Command centre", "Predict & prioritise", "Intervention studio", "Population intelligence", "Evidence & trust"])
        st.divider()
        st.caption("West Yorkshire · Leeds detailed pathway")
        st.caption("HTL private demonstration environment")
    return page


def command_centre(people: pd.DataFrame, events: pd.DataFrame, context: pd.DataFrame) -> None:
    hero("One operating view across a connected care pathway.", "PIE turns fragmented events into a practical picture of responsibility, next action, confidence and emerging demand across West Yorkshire.")
    pending = int(people.care_owner.eq("Receiving service not yet confirmed").sum())
    overdue = int(people.due_status.eq("Overdue").sum())
    priority = int(people.priority_band.eq("Priority 1").sum())
    forecast = int((people.review_opportunity_30d_pct >= 55).sum())
    for col, item in zip(st.columns(4), [("Priority action queue", priority, "modelled operational + review signal"), ("Ownership to confirm", pending, "handover requires acceptance"), ("Actions beyond due time", overdue, "pathway clock requires attention"), ("30-day review opportunities", forecast, "proactive workload forecast")]):
        with col: metric(*item)
    st.markdown("### What changes for teams")
    st.markdown("<div class='callout'>Rather than asking people to chase information across systems, PIE proposes a shared view of the pathway: <strong>what changed, who owns the next action, what needs doing first and how confident the team can be in the signal.</strong></div>", unsafe_allow_html=True)
    summary = people.groupby("place", as_index=False).agg(
        Active_cases=("person_key", "count"),
        Priority_1=("priority_band", lambda s: int((s == "Priority 1").sum())),
        Ownership_gaps=("care_owner", lambda s: int((s == "Receiving service not yet confirmed").sum())),
        Forecast_review=("review_opportunity_30d_pct", lambda s: int((s >= 55).sum())),
    )
    fig = px.bar(summary, x="place", y="Forecast_review", color="Priority_1", text="Active_cases", color_continuous_scale="Blues")
    fig.update_layout(title="Modelled proactive review workload by place", xaxis_title="", yaxis_title="Synthetic people meeting review threshold", coloraxis_colorbar_title="Priority 1")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("### Strategic fit")
    st.markdown("The design follows Stephen’s preferred separation of **devices**, **data storage** and a distinct **presentation and intelligence** layer. PIE is demonstrated in that third layer, supporting local services and established infrastructure rather than replacing them.")
    footer()


def predict_prioritise(people: pd.DataFrame) -> None:
    hero("Predict where attention will matter most.", "A transparent prioritisation model combines pathway reliability with guideline-informed review signals, so care teams can focus their next conversation and action.")
    c1, c2, c3 = st.columns(3)
    with c1: place = st.selectbox("Place", ["All West Yorkshire"] + sorted(people.place.unique().tolist()))
    with c2: pathway = st.multiselect("Pathway", sorted(people.pathway.unique()), default=sorted(people.pathway.unique()))
    with c3: band = st.multiselect("Priority", ["Priority 1", "Priority 2", "Priority 3", "Routine"], default=["Priority 1", "Priority 2", "Priority 3", "Routine"])
    view = people[people.pathway.isin(pathway) & people.priority_band.isin(band)].copy()
    if place != "All West Yorkshire": view = view[view.place.eq(place)]
    view = view.sort_values(["priority_band", "operational_priority_score", "review_opportunity_30d_pct"], ascending=[True, False, False])
    st.markdown("### Prioritised review queue")
    display = view[["person_key", "place", "pathway", "current_state", "care_owner", "next_action", "due_status", "source_freshness", "operational_priority_score", "review_opportunity_30d_pct", "top_explainers", "evidence_tags"]].copy()
    display.columns = ["PIE person key", "Place", "Pathway", "Current state", "Current owner", "Recommended next action", "Action clock", "Data confidence", "Operational score", "30-day review opportunity", "Why this has surfaced", "Evidence basis"]
    st.dataframe(display, use_container_width=True, hide_index=True)
    left, right = st.columns(2)
    with left:
        fig = px.histogram(view, x="review_opportunity_30d_pct", color="priority_band", nbins=16, barmode="overlay", color_discrete_sequence=[PIE_MAGENTA, PIE_DEEP, PIE_BLUE, "#9EADBC"])
        fig.update_layout(title="Modelled 30-day review opportunity", xaxis_title="Probability (%)", yaxis_title="Synthetic people")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown("### Explainable by design")
        st.write("Each surfaced case is accompanied by its leading signals, the action type and the guidance family behind the review logic. The operational score is separate from the clinical-context model: a missing owner or overdue action can drive priority even when there is no deterioration signal.")
        for tag in ["NICE NG249", "NICE NG136", "NICE NG196", "NICE NG106", "NHS England virtual wards", "Neighbourhood health"]:
            st.markdown(f"<span class='small-tag'>{tag}</span>", unsafe_allow_html=True)
    footer()


def intervention_studio(people: pd.DataFrame) -> None:
    hero("Test the impact of a different service response.", "A scenario environment for exploring which improvements could move more people into a safe, owned and proactive pathway before a real-world pilot is commissioned.")
    st.caption("Choose practical levers. PIE recalculates expected workload and pathway reliability in the synthetic model.")
    col1, col2, col3 = st.columns(3)
    with col1: handover = st.slider("Improve accepted handovers", 0, 100, 25, 5, help="Increase in the proportion of unresolved handovers accepted within the agreed window.")
    with col2: monitoring = st.slider("Expand targeted monitoring review", 0, 100, 20, 5, help="Additional coverage for people whose synthetic model flags a monitoring review opportunity.")
    with col3: medicines = st.slider("Increase medicines review capacity", 0, 100, 15, 5, help="Additional completion capacity for people with a review due.")
    ownership_gap = int(people.care_owner.eq("Receiving service not yet confirmed").sum())
    high_review = int((people.review_opportunity_30d_pct >= 55).sum())
    medicine_due = int(people.pathway.eq("Medicines optimisation").sum())
    closed = round(ownership_gap * handover / 100)
    reviewed = round(high_review * monitoring / 100)
    med_completed = round(medicine_due * medicines / 100)
    for col, item in zip(st.columns(4), [("Handover gaps resolved", closed, "within the scenario window"), ("Proactive reviews enabled", reviewed, "additional modelled capacity"), ("Medicines reviews completed", med_completed, "additional modelled capacity"), ("Remaining priority queue", max(0, int(people.priority_band.eq("Priority 1").sum()) - closed - round(reviewed * .25)), "synthetic scenario output")]):
        with col: metric(*item)
    st.markdown("### AI-supported service design")
    st.markdown("<div class='callout'>The AI role is not to decide treatment. It is to help teams model demand, surface people who may benefit from earlier review, explain why, and test how service capacity or pathway changes could alter the queue.</div>", unsafe_allow_html=True)
    scenario = pd.DataFrame({"Intervention": ["Accepted handovers", "Targeted monitoring reviews", "Medicines review capacity"], "Modelled additional actions": [closed, reviewed, med_completed]})
    fig = px.bar(scenario, x="Intervention", y="Modelled additional actions", text="Modelled additional actions", color="Intervention", color_discrete_sequence=[PIE_DEEP, PIE_BLUE, PIE_MAGENTA])
    fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Actions within scenario")
    st.plotly_chart(fig, use_container_width=True)
    footer()


def population_intelligence(people: pd.DataFrame, context: pd.DataFrame) -> None:
    hero("Use population evidence to plan a fairer pathway.", "Public demographic, deprivation, prescribing and admissions sources calibrate the context. Synthetic person-level scenarios make the operating model tangible without exposing real people.")
    left, right = st.columns(2)
    with left:
        age = people.groupby(["place", "age_band"], as_index=False).size().rename(columns={"size": "Synthetic people"})
        fig = px.bar(age, x="place", y="Synthetic people", color="age_band", barmode="stack", color_discrete_sequence=["#9EADBC", PIE_BLUE, PIE_DEEP, PIE_MAGENTA])
        fig.update_layout(title="Calibrated-sample age structure", xaxis_title="", yaxis_title="Synthetic people")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        imd = people.groupby(["place", "imd_quintile"], as_index=False).size().rename(columns={"size": "Synthetic people"})
        fig = px.bar(imd, x="place", y="Synthetic people", color="imd_quintile", barmode="stack", color_continuous_scale="PuBu")
        fig.update_layout(title="Area deprivation context within the synthetic sample", xaxis_title="", yaxis_title="Synthetic people")
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("### From population insight to pathway design")
    st.write("The regional view is designed to reveal whether priority, response capacity and access routes are aligned. SDOH fields shape how an offer is delivered, for example a non-digital route, interpreter support, carer contact or proactive outreach. They do not determine an individual outcome.")
    st.dataframe(context.rename(columns={"synthetic_sample": "Synthetic sample", "population_weight": "Population weight", "evidence_basis": "Calibration basis", "context_status": "Status"}), use_container_width=True, hide_index=True)
    footer()


def evidence_trust(people: pd.DataFrame, evidence: pd.DataFrame) -> None:
    hero("Evidence, identity and trust are built in.", "A compact demonstration view, backed by a transparent methodology: public data for population context, published guidance for review logic and synthetic records for person-level workflow.")
    st.markdown("### Evidence catalogue")
    st.dataframe(evidence[["layer", "source", "purpose", "status", "use_in_demo"]], use_container_width=True, hide_index=True)
    left, right = st.columns(2)
    with left:
        st.markdown("### Pseudonymisation design")
        st.write("The interface uses only an opaque **PIE person key**. In a future authorised deployment, a tenant-held pseudonymisation service could create a stable key from an NHS number using a cryptographic HMAC and retain the re-identification mapping separately behind role-based access. PIE would work with the key, not display the NHS number.")
    with right:
        st.markdown("### AI capability boundary")
        st.write("The demonstrator shows transparent, feature-based review prioritisation, demand forecasting and intervention simulation. A production model would require local validation, bias and performance testing, clinical safety governance and monitoring before it was used to influence care delivery.")
    st.markdown("### Current model structure")
    st.markdown("- **Operational intelligence:** ownership, action clock, source freshness and communication status\n- **Guideline-informed review opportunity:** evidence-tagged features and transparent explainers\n- **Population intelligence:** public-source calibration at place and small-area level\n- **Scenario analytics:** capacity and pathway-change modelling\n- **AI synthesis:** concise, explainable summaries for an MDT or operational lead")
    footer()


def main() -> None:
    st.set_page_config(page_title="PIE | West Yorkshire Connected Care", page_icon="◌", layout="wide")
    apply_brand()
    people, events, context, evidence = load_data()
    page = sidebar()
    if page == "Command centre": command_centre(people, events, context)
    elif page == "Predict & prioritise": predict_prioritise(people)
    elif page == "Intervention studio": intervention_studio(people)
    elif page == "Population intelligence": population_intelligence(people, context)
    else: evidence_trust(people, evidence)


if __name__ == "__main__":
    main()
