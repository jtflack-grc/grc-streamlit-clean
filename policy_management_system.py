#!/usr/bin/env python3
"""Policy Management System — sample workshop toy."""

from __future__ import annotations

import datetime
from datetime import timedelta

import numpy as np
import pandas as pd
import streamlit as st

import demo_kit
import portfolio_skin

st.set_page_config(
    page_title="Policy Management System · i on GRC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

portfolio_skin.apply(hide_sidebar=False)


def generate_sample_data(seed: int) -> list[dict]:
    rng = np.random.default_rng(seed)
    policy_types = [
        "Information Security Policy",
        "Access Control Policy",
        "Data Protection Policy",
        "Acceptable Use Policy",
        "Incident Response Policy",
    ]
    statuses = ["Draft", "Under Review", "Approved", "Published"]
    categories = ["Security", "Compliance", "Operations"]
    risks = ["Low", "Medium", "High", "Critical"]

    policies = []
    for i in range(15):
        created = datetime.datetime.now() - timedelta(days=int(rng.integers(30, 365)))
        policies.append(
            {
                "id": f"POL-{2024:04d}-{i + 1:03d}",
                "title": str(rng.choice(policy_types)),
                "version": f"{int(rng.integers(1, 5))}.{int(rng.integers(0, 9))}",
                "category": str(rng.choice(categories)),
                "status": str(rng.choice(statuses)),
                "owner": f"Department {int(rng.integers(1, 5))}",
                "created_date": created,
                "review_date": created + timedelta(days=365),
                "risk_level": str(rng.choice(risks)),
                "training_completion": int(rng.integers(40, 100)),
                "violations": int(rng.integers(0, 10)),
            }
        )

    policies.extend(
        [
            {
                "id": f"POL-{2024:04d}-{len(policies) + 1:03d}",
                "title": "IBM i Security Standard (QSECURITY / Special Authorities)",
                "version": "1.2",
                "category": "Security",
                "status": "Published",
                "owner": "IBM i Ops",
                "created_date": datetime.datetime.now() - timedelta(days=120),
                "review_date": datetime.datetime.now() + timedelta(days=245),
                "risk_level": "High",
                "training_completion": 72,
                "violations": 2,
            },
            {
                "id": f"POL-{2024:04d}-{len(policies) + 2:03d}",
                "title": "Mainframe Security Standard (RACF / z/OS)",
                "version": "2.0",
                "category": "Security",
                "status": "Approved",
                "owner": "Mainframe Security",
                "created_date": datetime.datetime.now() - timedelta(days=90),
                "review_date": datetime.datetime.now() + timedelta(days=275),
                "risk_level": "Critical",
                "training_completion": 65,
                "violations": 1,
            },
        ]
    )
    return policies


def _sync_policies(seed: int) -> None:
    if st.session_state.get("_policy_seed") != seed or "policies" not in st.session_state:
        st.session_state.policies = generate_sample_data(seed)
        st.session_state._policy_seed = seed


def _advance_status(status: str) -> str:
    order = ["Draft", "Under Review", "Approved", "Published"]
    if status not in order or status == order[-1]:
        return status
    return order[order.index(status) + 1]


def calculate_metrics(policies: list[dict]) -> dict:
    df = pd.DataFrame(policies)
    return {
        "total_policies": len(policies),
        "active_policies": int(df["status"].isin(["Approved", "Published"]).sum()),
        "draft_policies": int((df["status"] == "Draft").sum()),
        "avg_training_completion": float(df["training_completion"].mean()),
        "total_violations": int(df["violations"].sum()),
    }


def main():
    portfolio_skin.page_header(
        title="Policy Management System",
        lede="Sample policy inventory with status workflow and light analytics.",
        kicker="Governance",
    )

    with st.sidebar:
        st.header("Controls")
        seed = demo_kit.seed_controls()
        st.markdown("---")
        status_filter = st.multiselect(
            "Status",
            ["Draft", "Under Review", "Approved", "Published"],
            default=["Draft", "Under Review", "Approved", "Published"],
        )
        risk_filter = st.multiselect(
            "Risk level",
            ["Low", "Medium", "High", "Critical"],
            default=["Low", "Medium", "High", "Critical"],
        )
        category_filter = st.multiselect(
            "Category",
            ["Security", "Compliance", "Operations"],
            default=["Security", "Compliance", "Operations"],
        )

    _sync_policies(seed)
    df = pd.DataFrame(st.session_state.policies)
    view = df[
        df["status"].isin(status_filter)
        & df["risk_level"].isin(risk_filter)
        & df["category"].isin(category_filter)
    ].copy()

    metrics = calculate_metrics(view.to_dict("records") if not view.empty else [])
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Policies (filtered)", metrics["total_policies"] if view is not None else 0)
    c2.metric("Active", metrics["active_policies"])
    c3.metric("Draft", metrics["draft_policies"])
    c4.metric("Avg training", f"{metrics['avg_training_completion']:.1f}%")

    tab_dash, tab_manage, tab_analytics, tab_export = st.tabs(
        ["Dashboard", "Manage", "Analytics", "Export"]
    )

    with tab_dash:
        if view.empty:
            st.info("No policies match the sidebar filters.")
        else:
            left, right = st.columns(2)
            with left:
                st.bar_chart(view["status"].value_counts())
                st.caption("Status distribution")
            with right:
                st.bar_chart(view["risk_level"].value_counts())
                st.caption("Risk levels")

    with tab_manage:
        with st.expander("Add policy", expanded=False):
            with st.form("new_policy"):
                title = st.text_input("Policy title")
                category = st.selectbox("Category", ["Security", "Compliance", "Operations"])
                owner = st.text_input("Owner", value="Department 1")
                risk = st.selectbox("Risk level", ["Low", "Medium", "High", "Critical"], index=1)
                if st.form_submit_button("Create"):
                    if title.strip():
                        st.session_state.policies.append(
                            {
                                "id": f"POL-{datetime.datetime.now().year:04d}-{len(st.session_state.policies) + 1:03d}",
                                "title": title.strip(),
                                "version": "1.0",
                                "category": category,
                                "status": "Draft",
                                "owner": owner or "Unassigned",
                                "created_date": datetime.datetime.now(),
                                "review_date": datetime.datetime.now() + timedelta(days=365),
                                "risk_level": risk,
                                "training_completion": 0,
                                "violations": 0,
                            }
                        )
                        st.success("Policy created")
                        st.rerun()

        if view.empty:
            st.info("No policies to manage under current filters.")
        else:
            for _, policy in view.iterrows():
                with st.expander(f"{policy['id']} — {policy['title']}"):
                    a, b, c = st.columns(3)
                    a.write(f"**Status:** {policy['status']}")
                    a.write(f"**Category:** {policy['category']}")
                    b.write(f"**Owner:** {policy['owner']}")
                    b.write(f"**Risk:** {policy['risk_level']}")
                    c.write(f"**Training:** {policy['training_completion']}%")
                    c.write(f"**Violations:** {policy['violations']}")
                    if st.button(
                        "Advance status",
                        key=f"adv_{policy['id']}",
                        disabled=policy["status"] == "Published",
                    ):
                        for i, p in enumerate(st.session_state.policies):
                            if p["id"] == policy["id"]:
                                st.session_state.policies[i]["status"] = _advance_status(
                                    p["status"]
                                )
                                break
                        st.rerun()

    with tab_analytics:
        if view.empty:
            st.info("Nothing to chart.")
        else:
            left, right = st.columns(2)
            with left:
                st.write("Training completion by category")
                st.bar_chart(view.groupby("category")["training_completion"].mean())
            with right:
                st.write("Violations by risk level")
                st.bar_chart(view.groupby("risk_level")["violations"].sum())

    with tab_export:
        export_df = view.copy()
        for col in ("created_date", "review_date"):
            if col in export_df.columns:
                export_df[col] = export_df[col].astype(str)
        demo_kit.csv_download(export_df, "policies_filtered.csv", label="Download filtered policies")


if __name__ == "__main__":
    main()
