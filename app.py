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

PIE_DEEP = "#074695"
PIE_BLUE = "#0E74BA"
PIE_MAGENTA = "#BE3F89"
PIE_INK = "#0B2747"
PIE_SLATE = "#4E657D"


def ensure_demo_data() -> None:
    """Create fixed-seed synthetic outputs for a fresh clone."""
    required = [DATA_DIR / "synthetic_population.csv", DATA_DIR / "synthetic_events.csv", DATA_DIR / "place_context.csv"]
    if all(path.exists() for path in required):
        return
    subprocess.run([sys.executable, str(GENERATOR)], check=True, cwd=str(ROOT))


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ensure_demo_data()
    people = pd.read_csv(DATA_DIR / "synthetic_population.csv", parse_dates=["next_action_due"])
    events = pd.read_csv(DATA_DIR / "synthetic_events.csv", parse_dates=["event_time", "received_time"])
    context = pd.read_csv(DATA_DIR / "place_context.csv")
    return people, events, context


def apply_brand() -> None:
    st.markdown(f"""
    <style>
    .stApp {{ background: linear-gradient(180deg, #F6FAFE 0%, #FFFFFF 34%); }}
    .block-container {{ max-width: 1440px; padding-top: 1.4rem; padding-bottom: 2.2rem; }}
    [data-testid="stSidebar"] {{ background: #FFFFFF; border-right: 1px solid #DDE8F3; }}
    h1, h2, h3 {{ color: {PIE_INK}; letter-spacing: -0.025em; }}
    .eyebrow {{ color: {PIE_MAGENTA}; font-size: .73rem; font-weight: 800; letter-spacing: .13em; text-transform: uppercase; }}
    .hero {{ border: 1px solid #D5E5F3; border-radius: 22px; padding: 1.35rem 1.5rem; margin-bottom: 1rem; background: radial-gradient(circle at 92% 12%, rgba(190,63,137,.11), transparent 25%), linear-gradient(120deg, #FFFFFF, #EDF6FD); }}
    .hero h1 {{ margin: .2rem 0 .45rem; font-size: clamp(2rem, 3vw, 3.15rem); }}
    .hero p {{ margin: 0; color: {PIE_SLATE}; font-size: 1.05rem; max-width: 950px; }}
    .metric-card {{ border: 1px solid #DCE8F5; background: #FFFFFF; border-radius: 16px; min-height: 116px; padding: .9rem 1rem; box-shadow: 0 8px 24px rgba(22, 76, 130, .04); }}
    .metric-label {{ color: {PIE_SLATE}; font-size: .78rem; font-weight: 700; }}
    .metric-value {{ color: {PIE_DEEP}; font-size: 1.9rem; font-weight: 800; line-height: 1.12; margin: .35rem 0 .2rem; }}
    .metric-sub {{ color: {PIE_SLATE}; font-size: .76rem; }}
    .callout {{ border-left: 4px solid {PIE_MAGENTA}; border-radius: 0 12px 12px 0; background: #FFF9FD; padding: .9rem 1rem; color: {PIE_INK}; }}
    .governance {{ border: 1px dashed #B9CAE0; border-radius: 12px; background: #FBFCFE; padding: .85rem 1rem; color: {PIE_SLATE}; font-size: .88rem; }}
    </style>
    """, unsafe_allow_html=True)


def hero(title: str, subtitle: str) -> None:
    st.markdown(f"<div class='hero'><div class='eyebrow'>PIE | West Yorkshire Connected Care</div><h1>{title}</h1><p>{subtitle}</p></div>", unsafe_allow_html=True)


def metric(label: str, value: int | str, subtitle: str) -> None:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div><div class='metric-sub'>{subtitle}</div></div>", unsafe_allow_html=True)


def governance_banner() -> None:
    st.markdown("<div class='governance'><strong>Evidence boundary:</strong> This is a synthetic demonstrator. It contains no patient, service-user or live operational data. Public sources inform the future calibration method only. Current pathway states, timestamps, ownership and exceptions are illustrative, not a claim about West Yorkshire performance.</div>", unsafe_allow_html=True)


def sidebar() -> str:
    with st.sidebar:
        if LOGO.exists():
            st.image(str(LOGO), width=92)
        st.markdown("### PIE™")
        st.caption("Patient Insight Engine")
        st.divider()
        page = st.radio("Navigate", ["West Yorkshire system view", "Care coordination", "Leeds frailty & TEC", "Population, equity & signals", "Data calibration & governance"])
        st.divider()
        st.caption("HTL private synthetic demonstrator")
        st.caption("No live NHS or local-authority integration")
    return page


def overview(people: pd.DataFrame, context: pd.DataFrame) -> None:
    hero("See the state of care, not just a record of activity.", "A regional, person-led operating-model demonstrator for making ownership, next actions, source confidence and exceptions visible across West Yorkshire.")
    governance_banner()
    kpis = [
        ("Synthetic active pathways", len(people), "Illustrative working cohort"),
        ("Critical exceptions", int(people.priority.eq("Critical").sum()), "Synthetic cases needing attention"),
        ("Awaiting acceptance", int(people.current_state.eq("Awaiting handover acceptance").sum()), "Ownership transfer incomplete"),
        ("Overdue actions", int(people.action_status.eq("Overdue").sum()), "Against illustrative action clocks"),
        ("Freshness flags", int(~people.data_freshness.eq("Current").sum()), "Signal needs a confidence check"),
    ]
    for col, item in zip(st.columns(5), kpis):
        with col:
            metric(*item)
    st.markdown("### The operating-model question")
    st.markdown("<div class='callout'>West Yorkshire already has local services, teams and data assets. PIE is not presented as a replacement record. It tests whether a shared operating view can show <strong>what happened, who accepted responsibility, what must happen next, by when, how current the information is and whether the person has been told</strong>.</div>", unsafe_allow_html=True)
    left, right = st.columns([1.15, .85])
    with left:
        st.markdown("### What PIE is demonstrating")
        st.markdown("- a potential care-state and coordination layer alongside authorised systems\n- accountable owner and action clock\n- the difference between an event being recorded, accepted, completed and communicated\n- exception and reporting-confidence views\n- public population and inequality context alongside an operational model")
    with right:
        st.markdown("### What it is not")
        st.markdown("- a live NHS, local-authority or shared-care-record deployment\n- a clinical decision-maker or substitute for professional judgement\n- evidence that any existing system lacks a specific function\n- an estimate of actual pathway volumes or performance")
    place_summary = people.groupby("place", as_index=False).agg(Synthetic_pathways=("synthetic_person_id", "count"), Critical_exceptions=("priority", lambda x: int((x == "Critical").sum())))
    fig = px.bar(place_summary, x="place", y="Synthetic_pathways", color="Critical_exceptions", text="Synthetic_pathways", color_continuous_scale="Blues")
    fig.update_layout(title="Illustrative synthetic pathways by West Yorkshire place", xaxis_title="", yaxis_title="Synthetic cases", coloraxis_colorbar_title="Critical")
    st.plotly_chart(fig, use_container_width=True)


def coordination(people: pd.DataFrame) -> None:
    hero("Make ownership and exception management visible.", "A synthetic control-room view of whether responsibility has been accepted, what action is due and where source confidence needs a check.")
    governance_banner()
    c1, c2, c3 = st.columns(3)
    with c1:
        place = st.selectbox("West Yorkshire place", ["All places"] + sorted(people.place.unique().tolist()))
    with c2:
        priority = st.multiselect("Priority", sorted(people.priority.unique().tolist()), default=sorted(people.priority.unique().tolist()))
    with c3:
        state = st.multiselect("Care state", sorted(people.current_state.unique().tolist()), default=sorted(people.current_state.unique().tolist()))
    view = people.copy()
    if place != "All places":
        view = view[view.place.eq(place)]
    view = view[view.priority.isin(priority) & view.current_state.isin(state)]
    st.markdown("### Action queue")
    st.dataframe(view.sort_values(["priority", "action_status", "next_action_due"])[["synthetic_person_id", "display_name", "place", "pathway", "current_state", "care_owner", "next_action", "action_status", "priority", "data_freshness", "person_notification"]], use_container_width=True, hide_index=True)
    by_state = view.groupby(["place", "current_state"], as_index=False).size().rename(columns={"size": "Synthetic cases"})
    fig = px.bar(by_state, x="place", y="Synthetic cases", color="current_state", barmode="stack", color_discrete_sequence=[PIE_DEEP, PIE_BLUE, PIE_MAGENTA, "#6A8AA6", "#84BFA7"])
    fig.update_layout(title="Illustrative care-state mix", xaxis_title="", yaxis_title="Synthetic cases")
    st.plotly_chart(fig, use_container_width=True)


def leeds_pathway(people: pd.DataFrame, events: pd.DataFrame) -> None:
    hero("Leeds frailty and TEC: a worked pathway narrative.", "Leeds is the first detailed lens, not the product boundary. This scenario shows how handover acceptance, action ownership, telecare context and person communication could be made visible.")
    governance_banner()
    cases = people[(people.place == "Leeds") & (people.pathway == "Post-discharge frailty")].copy()
    first = "PIE-WY-0001" if "PIE-WY-0001" in set(cases.synthetic_person_id) else cases.synthetic_person_id.iloc[0]
    case_id = st.selectbox("Synthetic scenario", cases.synthetic_person_id.tolist(), index=cases.synthetic_person_id.tolist().index(first), format_func=lambda x: cases.loc[cases.synthetic_person_id.eq(x), "display_name"].iloc[0])
    row = cases[cases.synthetic_person_id.eq(case_id)].iloc[0]
    for col, item in zip(st.columns(4), [("Care state", row.current_state, "Illustrative"), ("Current owner", row.care_owner, "Synthetic workflow"), ("Next action", row.next_action, row.action_status), ("Person notified", row.person_notification, "Synthetic status")]):
        with col:
            metric(*item)
    st.markdown("### Context, not a deterministic risk score")
    st.write(f"**{row.display_name}** is an illustrative {row.age}-year-old scenario in {row.locality}. The synthetic context shows: **{row.living_arrangement.lower()}**, {row.disability_context.lower()}, IMD quintile {row.imd_quintile} and **{row.digital_access_context.lower()}**. These fields shape a service response in the demonstrator. They do not determine an individual outcome or replace clinical and person-led assessment.")
    timeline = events[events.synthetic_person_id.eq(case_id)].sort_values("event_time")
    fig = px.scatter(timeline, x="event_time", y="event_type", color="quality", hover_data=["source_system", "mode", "received_time"], color_discrete_sequence=[PIE_MAGENTA, PIE_BLUE, "#E5962E"])
    fig.update_layout(title="Synthetic pathway event sequence", xaxis_title="Event time", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)


def population_equity(people: pd.DataFrame, context: pd.DataFrame) -> None:
    hero("Population context supports a fairer operating model.", "The demonstrator keeps area-level context separate from operational action. Current values are illustrative and awaiting calibration from dated public extracts.")
    governance_banner()
    col1, col2 = st.columns(2)
    with col1:
        age = people.groupby(["place", "age_band"], as_index=False).size().rename(columns={"size": "Synthetic people"})
        fig = px.bar(age, x="place", y="Synthetic people", color="age_band", barmode="stack", color_discrete_sequence=[PIE_BLUE, PIE_DEEP, PIE_MAGENTA])
        fig.update_layout(title="Illustrative age-band distribution", xaxis_title="", yaxis_title="Synthetic people")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        imd = people.groupby(["place", "imd_quintile"], as_index=False).size().rename(columns={"size": "Synthetic people"})
        fig = px.bar(imd, x="place", y="Synthetic people", color="imd_quintile", barmode="stack", color_continuous_scale="PuBu")
        fig.update_layout(title="Illustrative deprivation-context distribution", xaxis_title="", yaxis_title="Synthetic people")
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("### Admissions, medicines and access signals")
    st.caption("All signals below are illustrative placeholders until public source extracts are added and validated. They are not performance measures.")
    melt = context.melt(id_vars=["place", "source_status"], value_vars=["inequalities_signal", "admissions_signal", "medicines_signal", "digital_access_signal"], var_name="Signal", value_name="Illustrative level")
    fig = px.bar(melt, x="place", y="Illustrative level", color="Signal", barmode="group", color_discrete_sequence=[PIE_MAGENTA, PIE_DEEP, PIE_BLUE, "#84BFA7"])
    fig.update_layout(xaxis_title="", yaxis_title="Illustrative level (1–5)")
    st.plotly_chart(fig, use_container_width=True)


def calibration_governance() -> None:
    hero("Evidence discipline is part of the product.", "The goal is not to disguise synthetic scenarios as local facts. The goal is to test the operating model safely, then calibrate aggregate distributions from dated public evidence.")
    governance_banner()
    st.markdown("### Source families for the next calibration stage")
    st.markdown("- ONS population estimates and Census / Nomis distributions\n- English Indices of Deprivation 2025\n- OHID Fingertips outcomes, including falls and readmission context\n- NHSBSA prescribing aggregates\n- NHS England published activity context\n- local observatories, JSNAs and West Yorkshire strategic material")
    st.markdown("### What public data can and cannot do")
    left, right = st.columns(2)
    with left:
        st.success("**Can support aggregate calibration**\n\nAge structure, household context, deprivation, disability and unpaid-care context, public-health indicators, prescribing aggregates and published admissions context.")
    with right:
        st.warning("**Cannot reveal live operations**\n\nWho needs action today, device status, current discharge, care ownership, accepted handovers, medicines review status or operational response times.")
    st.markdown("### Future pilot boundary")
    st.markdown("A future operational pilot would need an agreed use case, lawful basis, information-governance route, technical onboarding, clinical-safety work where applicable, human oversight, auditability and local validation of definitions. No entitlement to shared-record, telecare or other live-system APIs is assumed by this demonstrator.")


def main() -> None:
    st.set_page_config(page_title="PIE | West Yorkshire Connected Care", page_icon="◌", layout="wide")
    apply_brand()
    page = sidebar()
    people, events, context = load_data()
    if page == "West Yorkshire system view":
        overview(people, context)
    elif page == "Care coordination":
        coordination(people)
    elif page == "Leeds frailty & TEC":
        leeds_pathway(people, events)
    elif page == "Population, equity & signals":
        population_equity(people, context)
    else:
        calibration_governance()


if __name__ == "__main__":
    main()
