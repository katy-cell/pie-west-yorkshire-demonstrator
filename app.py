from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from pie_model import MODEL_VERSION, build_model

st.set_page_config(page_title="PIE | West Yorkshire Connected Care", page_icon="◌", layout="wide")

ROOT = Path(__file__).resolve().parent
LOGO = ROOT / "assets" / "branding" / "pie_logo_mark_rgb.jpg"

PIE_DEEP = "#074695"
PIE_BLUE = "#0E74BA"
PIE_MAGENTA = "#BE3F89"
PIE_INK = "#0B2747"
PIE_SLATE = "#4E657D"
PIE_MIST = "#F7FAFE"


@st.cache_data(show_spinner=False)
def load_model() -> dict[str, pd.DataFrame]:
    """Build the versioned model in memory: no cached CSV files or stale schemas."""
    return build_model()


def apply_brand() -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{ background: linear-gradient(180deg, {PIE_MIST} 0%, #FFFFFF 39%); }}
        .block-container {{ max-width: 1500px; padding-top: 1.1rem; padding-bottom: 1.5rem; }}
        [data-testid="stSidebar"] {{ background: #FFFFFF; border-right: 1px solid #DDE8F3; }}
        h1,h2,h3 {{ color: {PIE_INK}; letter-spacing: -.03em; }}
        .eyebrow {{ color: {PIE_MAGENTA}; font-weight: 800; text-transform: uppercase; letter-spacing: .13em; font-size: .72rem; }}
        .hero {{ border: 1px solid #D6E4F4; border-radius: 22px; padding: 1.35rem 1.5rem; margin-bottom: 1.1rem; background: radial-gradient(circle at 92% 12%, rgba(190,63,137,.13), transparent 24%), linear-gradient(120deg, #FFFFFF, #EEF6FD); }}
        .hero h1 {{ margin: .15rem 0 .45rem; font-size: clamp(2rem, 3vw, 3.2rem); }}
        .hero p {{ margin: 0; max-width: 1020px; color: {PIE_SLATE}; font-size: 1.03rem; }}
        .metric-card {{ border: 1px solid #DDE8F5; border-radius: 15px; background: #FFFFFF; min-height: 112px; padding: .9rem 1rem; box-shadow: 0 8px 22px rgba(22,76,130,.045); }}
        .metric-label {{ color: {PIE_SLATE}; font-size: .75rem; font-weight: 750; }}
        .metric-value {{ color: {PIE_DEEP}; font-size: 1.78rem; font-weight: 820; line-height: 1.14; margin: .3rem 0 .16rem; }}
        .metric-sub {{ color: {PIE_SLATE}; font-size: .76rem; }}
        .callout {{ border-left: 4px solid {PIE_MAGENTA}; border-radius: 0 12px 12px 0; background: #FFF9FD; padding: .9rem 1rem; color: {PIE_INK}; }}
        .arch-card {{ border: 1px solid #DDE8F5; border-radius: 14px; background: #FFFFFF; padding: .95rem 1rem; margin-bottom: .65rem; }}
        .arch-title {{ color: {PIE_DEEP}; font-weight: 800; font-size: .95rem; margin-bottom: .35rem; }}
        .arch-meta {{ color: {PIE_SLATE}; font-size: .82rem; margin-top:.24rem; }}
        .tag {{ display:inline-block; border:1px solid #D8E6F2; border-radius:999px; background:#FFFFFF; padding:.22rem .55rem; color:{PIE_SLATE}; font-size:.72rem; margin:0 .35rem .35rem 0; }}
        .footer {{ margin-top: 2rem; padding-top: .75rem; border-top: 1px solid #E3EBF5; color: #6B7F95; font-size: .73rem; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str) -> None:
    st.markdown(
        f"<div class='hero'><div class='eyebrow'>PIE | West Yorkshire Connected Care</div><h1>{title}</h1><p>{subtitle}</p></div>",
        unsafe_allow_html=True,
    )


def metric(label: str, value: int | str, subtitle: str) -> None:
    st.markdown(
        f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div><div class='metric-sub'>{subtitle}</div></div>",
        unsafe_allow_html=True,
    )


def footer() -> None:
    st.markdown(
        "<div class='footer'>PIE™ West Yorkshire Connected Care · published population baseline and evidence framework · modelled care opportunities and operational exemplars · no live patient, service-user or operational data</div>",
        unsafe_allow_html=True,
    )


def empty_state(message: str) -> None:
    st.info(message, icon="◌")


def sidebar() -> str:
    with st.sidebar:
        if LOGO.exists():
            st.image(str(LOGO), width=92)
        st.markdown("### PIE™")
        st.caption("Patient Insight Engine")
        st.divider()
        page = st.radio(
            "Navigate",
            [
                "PIE command centre",
                "Predict and act",
                "Intervention studio",
                "Population and equity",
                "Architecture and assurance",
            ],
        )
        st.divider()
        st.caption("West Yorkshire system view")
        st.caption("Leeds frailty and TEC pathway lens")
        st.caption(f"Model release {MODEL_VERSION}")
    return page


def command_centre(population: pd.DataFrame, forecast: pd.DataFrame) -> None:
    hero(
        "From fragmented data to accountable action.",
        "PIE is a care-state, orchestration and intelligence layer. It models where attention is likely to matter next, makes the reason visible and supports teams to act across organisational boundaries.",
    )
    total_population = int(population["population"].sum())
    opportunities = int(forecast["expected_30d"].sum())
    priority = int(forecast["priority_30d"].sum())
    transitions = int(round(forecast.loc[forecast["pathway"] == "Post-discharge coordination", "expected_30d"].sum() * 0.37))
    cards = [
        ("West Yorkshire population", f"{total_population:,}", "published 2024 resident population baseline"),
        ("30-day care opportunities", f"{opportunities:,}", "modelled from public baseline and pathway scenario rates"),
        ("Priority attention windows", f"{priority:,}", "modelled opportunities requiring earlier co-ordination"),
        ("Transition friction signals", f"{transitions:,}", "modelled post-discharge ownership / follow-up focus"),
    ]
    for col, item in zip(st.columns(4), cards):
        with col:
            metric(*item)

    st.markdown("### The PIE operating question")
    st.markdown(
        "<div class='callout'><strong>What changed, who owns the next action, what should happen next, by when and what is most likely to worsen if no-one acts?</strong> PIE connects those questions to a visible care state, an explainable signal and an action route.</div>",
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.25, 1])
    with left:
        by_place = forecast.groupby(["place", "pathway"], as_index=False)["expected_30d"].sum()
        fig = px.bar(
            by_place,
            x="place",
            y="expected_30d",
            color="pathway",
            barmode="stack",
            color_discrete_sequence=[PIE_DEEP, PIE_BLUE, PIE_MAGENTA, "#58748F"],
        )
        fig.update_layout(
            title="Expected 30-day care opportunities by place and pathway",
            xaxis_title="",
            yaxis_title="Modelled care opportunities",
            legend_title="Pathway",
        )
        st.plotly_chart(fig, use_container_width=True)
    with right:
        horizon = forecast.groupby("pathway", as_index=False)[["expected_7d", "expected_14d", "expected_30d"]].sum().melt(
            id_vars="pathway", var_name="horizon", value_name="opportunities"
        )
        horizon["horizon"] = horizon["horizon"].map({"expected_7d": "7 days", "expected_14d": "14 days", "expected_30d": "30 days"})
        fig = px.line(
            horizon,
            x="horizon",
            y="opportunities",
            color="pathway",
            markers=True,
            category_orders={"horizon": ["7 days", "14 days", "30 days"]},
            color_discrete_sequence=[PIE_DEEP, PIE_BLUE, PIE_MAGENTA, "#58748F"],
        )
        fig.update_layout(title="Forecast horizon", xaxis_title="", yaxis_title="Modelled opportunities")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### From source to action")
    sequence = [
        ("1", "Ingest", "Authorised EPR, primary care, community, device, prescribing and public-data inputs"),
        ("2", "Understand", "FHIR normalisation, terminology, pseudonymisation, provenance and care-state construction"),
        ("3", "Predict", "Explainable cohort signals, demand forecasting, risk and action prioritisation"),
        ("4", "Orchestrate", "Named owner, next action, deadline, notification and exception route"),
        ("5", "Learn", "Outcome feedback, fairness monitoring, pathway variation and service improvement"),
    ]
    cols = st.columns(5)
    for col, (number, label, description) in zip(cols, sequence):
        with col:
            st.markdown(f"<div class='arch-card'><div class='eyebrow'>{number}</div><div class='arch-title'>{label}</div><div class='arch-meta'>{description}</div></div>", unsafe_allow_html=True)
    footer()


def predict_and_act(work_items: pd.DataFrame, forecast: pd.DataFrame) -> None:
    hero(
        "Predict where attention will matter most.",
        "The control view combines population demand modelling, pathway state and evidence-backed review logic. It surfaces a focused action list rather than another static reporting queue.",
    )
    col1, col2, col3 = st.columns(3)
    places = sorted(work_items["place"].unique().tolist())
    pathways = sorted(work_items["pathway"].unique().tolist())
    with col1:
        selected_place = st.selectbox("Place", ["All West Yorkshire"] + places)
    with col2:
        selected_pathways = st.multiselect("Pathway", pathways, default=pathways)
    with col3:
        selected_window = st.multiselect("Attention window", ["0–7 days", "8–14 days", "15–30 days"], default=["0–7 days", "8–14 days", "15–30 days"])

    view = work_items.loc[
        work_items["pathway"].isin(selected_pathways) & work_items["attention_window"].isin(selected_window)
    ].copy()
    if selected_place != "All West Yorkshire":
        view = view.loc[view["place"] == selected_place].copy()
    if view.empty:
        empty_state("No modelled care opportunities match these selections. Adjust the pathway, place or attention-window filters.")
        footer()
        return

    view = view.sort_values(["priority", "pie_attention_index"], ascending=[True, False])
    selected_forecast = forecast.loc[forecast["pathway"].isin(selected_pathways)].copy()
    if selected_place != "All West Yorkshire":
        selected_forecast = selected_forecast.loc[selected_forecast["place"] == selected_place]
    urgent = int((view["priority"] == "Priority attention").sum())
    for col, item in zip(
        st.columns(3),
        [
            ("Modelled action records", f"{len(view):,}", "representative care-state and workflow exemplars"),
            ("Priority attention", f"{urgent:,}", "records ranked by pathway state and action need"),
            ("30-day pathway demand", f"{int(selected_forecast['expected_30d'].sum()):,}", "modelled care opportunities for current selection"),
        ],
    ):
        with col:
            metric(*item)

    st.markdown("### Action list")
    table = view[
        [
            "pie_work_item",
            "place",
            "pathway",
            "attention_window",
            "priority",
            "care_state",
            "pie_attention_index",
            "why_now",
            "recommended_next_action",
            "model_confidence",
        ]
    ].rename(
        columns={
            "pie_work_item": "PIE work item",
            "place": "Place",
            "pathway": "Pathway",
            "attention_window": "Attention window",
            "priority": "Priority",
            "care_state": "Care state",
            "pie_attention_index": "PIE attention index",
            "why_now": "Why now",
            "recommended_next_action": "Recommended action",
            "model_confidence": "Signal confidence",
        }
    )
    st.dataframe(table, use_container_width=True, hide_index=True)

    left, right = st.columns([1.1, 0.9])
    with left:
        selection = st.selectbox("Inspect a modelled operational record", view["pie_work_item"].tolist())
        detail = view.loc[view["pie_work_item"] == selection].iloc[0]
        st.markdown("### PIE operational synthesis")
        st.markdown(
            f"<div class='callout'><strong>{detail['care_state']}</strong><br><br>"
            f"This item has surfaced in the <strong>{detail['attention_window']}</strong> attention window for <strong>{detail['pathway']}</strong>. "
            f"PIE combines the available source chain, pathway state and evidence configuration to recommend: <strong>{detail['recommended_next_action']}</strong>.</div>",
            unsafe_allow_html=True,
        )
        st.caption(f"Evidence basis: {detail['evidence_basis']} · Source lineage: {detail['source_chain']}")
    with right:
        priority_counts = view.groupby(["pathway", "priority"], as_index=False).size().rename(columns={"size": "records"})
        fig = px.bar(
            priority_counts,
            x="pathway",
            y="records",
            color="priority",
            barmode="stack",
            color_discrete_map={"Priority attention": PIE_MAGENTA, "Planned review": PIE_BLUE},
        )
        fig.update_layout(title="Action-record mix", xaxis_title="", yaxis_title="Modelled records")
        st.plotly_chart(fig, use_container_width=True)
    footer()


def intervention_studio(forecast: pd.DataFrame) -> None:
    hero(
        "Test how a service change could alter the next 30 days.",
        "PIE does not only report pressure. It models practical choices, such as strengthening handover acceptance, expanding targeted monitoring or increasing medicines-review capacity, before a service commits to a pilot.",
    )
    first, second, third, fourth = st.columns(4)
    with first:
        handover = st.slider("Accepted handovers", 0, 100, 35, 5, help="Share of modelled transition friction addressed by a clearer acceptance workflow.")
    with second:
        monitoring = st.slider("Targeted monitoring capacity", 0, 100, 25, 5, help="Share of modelled CVD and frailty review opportunities brought forward.")
    with third:
        medicines = st.slider("Structured medicines reviews", 0, 100, 20, 5, help="Share of modelled medicines opportunities addressed earlier.")
    with fourth:
        tec = st.slider("TEC / home-first response", 0, 100, 25, 5, help="Share of modelled frailty and falls opportunities supported through a faster response.")

    post_discharge = int(forecast.loc[forecast["pathway"] == "Post-discharge coordination", "priority_30d"].sum())
    monitoring_pool = int(forecast.loc[forecast["pathway"].isin(["CVD remote monitoring", "Frailty, falls and TEC"]), "priority_30d"].sum())
    medicines_pool = int(forecast.loc[forecast["pathway"] == "Medicines optimisation", "priority_30d"].sum())
    frailty_pool = int(forecast.loc[forecast["pathway"] == "Frailty, falls and TEC", "priority_30d"].sum())
    handover_shift = int(round(post_discharge * handover / 100 * 0.48))
    monitoring_shift = int(round(monitoring_pool * monitoring / 100 * 0.32))
    medicines_shift = int(round(medicines_pool * medicines / 100 * 0.34))
    tec_shift = int(round(frailty_pool * tec / 100 * 0.30))
    total_shift = handover_shift + monitoring_shift + medicines_shift + tec_shift
    baseline_priority = int(forecast["priority_30d"].sum())
    remaining = max(0, baseline_priority - total_shift)

    cards = [
        ("Co-ordination actions brought forward", f"{handover_shift:,}", "modelled effect of stronger ownership acceptance"),
        ("Targeted reviews enabled", f"{monitoring_shift + medicines_shift:,}", "modelled capacity shift across monitoring and medicines"),
        ("Home-first response opportunities", f"{tec_shift:,}", "modelled frailty / TEC action shift"),
        ("Priority queue after scenario", f"{remaining:,}", "modelled residual attention requirement"),
    ]
    for col, item in zip(st.columns(4), cards):
        with col:
            metric(*item)

    scenario = pd.DataFrame(
        {
            "Measure": ["Baseline priority attention", "Brought forward through scenario", "Remaining priority attention"],
            "Modelled opportunities": [baseline_priority, total_shift, remaining],
        }
    )
    left, right = st.columns([1.15, 0.85])
    with left:
        fig = px.bar(
            scenario,
            x="Measure",
            y="Modelled opportunities",
            text="Modelled opportunities",
            color="Measure",
            color_discrete_sequence=[PIE_DEEP, PIE_MAGENTA, PIE_BLUE],
        )
        fig.update_layout(showlegend=False, title="Scenario effect on the 30-day action queue", xaxis_title="", yaxis_title="Modelled care opportunities")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown("### What the AI is doing")
        st.write(
            "PIE uses an explainable demand-and-care-state model to test the operational effect of a change. In a production implementation, the same layer would learn from observed pathway outcomes, capacity and service response, under clinical safety and model-governance controls."
        )
        st.markdown("<span class='tag'>Demand forecast</span><span class='tag'>Care-state orchestration</span><span class='tag'>Explainable prioritisation</span><span class='tag'>Scenario modelling</span>", unsafe_allow_html=True)
    footer()


def population_and_equity(population: pd.DataFrame, forecast: pd.DataFrame) -> None:
    hero(
        "Represent the region as it is, not as a balanced mock cohort.",
        "This view starts with published place populations and median ages. PIE then models expected care opportunities against that real regional shape, so variation by place is visible before live data is connected.",
    )
    left, right = st.columns(2)
    with left:
        fig = px.bar(
            population,
            x="place",
            y="population",
            text="population",
            color="median_age",
            color_continuous_scale="Blues",
        )
        fig.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig.update_layout(title="Published 2024 population by place", xaxis_title="", yaxis_title="Residents", coloraxis_colorbar_title="Median age")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        demand = forecast.groupby(["place", "pathway"], as_index=False)["opportunities_per_10k"].sum()
        fig = px.bar(
            demand,
            x="place",
            y="opportunities_per_10k",
            color="pathway",
            barmode="group",
            color_discrete_sequence=[PIE_DEEP, PIE_BLUE, PIE_MAGENTA, "#58748F"],
        )
        fig.update_layout(title="Expected opportunity rate per 10,000 residents", xaxis_title="", yaxis_title="Modelled 30-day opportunities per 10,000")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Published baseline and modelling inputs")
    baseline_view = population[["place", "population", "population_share", "median_age", "context", "published_baseline"]].copy()
    baseline_view["population_share"] = (baseline_view["population_share"] * 100).round(1).astype(str) + "%"
    baseline_view = baseline_view.rename(
        columns={
            "place": "Place",
            "population": "Published population",
            "population_share": "West Yorkshire share",
            "median_age": "Median age",
            "context": "Population context",
            "published_baseline": "Source",
        }
    )
    st.dataframe(baseline_view, use_container_width=True, hide_index=True)
    st.markdown("### Equity by design")
    st.markdown(
        "The production PIE model is designed to add protected and access-relevant variables only where there is a clear care or service-design purpose, such as non-digital access, interpreter need, carer involvement, rurality, deprivation context or barrier to follow-up. These fields should support fairer access and outreach, not become an automated decision about an individual."
    )
    footer()


def architecture_and_assurance(architecture: pd.DataFrame, evidence: pd.DataFrame) -> None:
    hero(
        "Show the full PIE proposition, not a standalone dashboard.",
        "This demonstrator represents the presentation, intelligence and scenario layer of PIE. The production architecture adds governed ingestion, interoperability, pseudonymisation, FHIR persistence, feature engineering, explainability and action orchestration.",
    )
    st.markdown("### Architecture-led product story")
    for _, row in architecture.iterrows():
        st.markdown(
            f"<div class='arch-card'><div class='arch-title'>{row['layer']}</div>"
            f"<div><strong>Production capability:</strong> {row['production_capability']}</div>"
            f"<div class='arch-meta'><strong>This demonstrator:</strong> {row['demonstrator_representation']}</div>"
            f"<div class='arch-meta'><strong>Value:</strong> {row['value']}</div></div>",
            unsafe_allow_html=True,
        )

    left, right = st.columns([1.1, 0.9])
    with left:
        st.markdown("### AI capabilities represented here")
        capabilities = pd.DataFrame(
            [
                {"Capability": "Care-state intelligence", "What it answers": "What changed, who owns the next action, what is due and what has not been accepted?"},
                {"Capability": "Population demand forecasting", "What it answers": "What care opportunities are expected across 7, 14 and 30 days by place and pathway?"},
                {"Capability": "Explainable prioritisation", "What it answers": "Why has a work item surfaced and what evidence / signal chain supports it?"},
                {"Capability": "Intervention simulation", "What it answers": "How could changes in handovers, monitoring, medicines or TEC capacity shift the queue?"},
                {"Capability": "Ambient and unstructured-data pathway", "What it answers": "How could approved speech / text extraction create structured observations, tasks and care-state updates?"},
            ]
        )
        st.dataframe(capabilities, use_container_width=True, hide_index=True)
    with right:
        st.markdown("### Production boundary")
        st.write(
            "The architecture supports integration with approved sources and outputs such as EPRs, primary-care systems, public data, community systems, remote-monitoring devices and partner reporting. This Streamlit environment is deliberately only the presentation and simulation layer: it is not connected to NHS FDP, a shared-care record, HAPI FHIR, AWS, or a live service workflow."
        )
        st.markdown("### Identity pattern")
        st.write(
            "A future authorised deployment would use a tenant-held pseudonymisation service to create a stable PIE key from an NHS number. The re-identification mapping would remain separate, access-controlled and outside the analytics / presentation layer. The app therefore shows only opaque work-item keys."
        )

    st.markdown("### Evidence catalogue")
    st.dataframe(evidence, use_container_width=True, hide_index=True)
    footer()


def main() -> None:
    apply_brand()
    model = load_model()
    page = sidebar()
    if page == "PIE command centre":
        command_centre(model["population"], model["forecast"])
    elif page == "Predict and act":
        predict_and_act(model["work_items"], model["forecast"])
    elif page == "Intervention studio":
        intervention_studio(model["forecast"])
    elif page == "Population and equity":
        population_and_equity(model["population"], model["forecast"])
    else:
        architecture_and_assurance(model["architecture"], model["evidence"])


if __name__ == "__main__":
    main()
