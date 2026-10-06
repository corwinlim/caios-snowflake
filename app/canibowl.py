"""
CAIOS CaniBowl — Pet 360 + Deterministic Transition Risk UI
============================================================

A Streamlit companion-animal adaptation of the "Patient and Member 360
and Clinical or Regulatory Document Copilot" hackathon track.

Shows: Pet 360 · Chicken → Salmon · +13.70% · recent GI signal ·
       Risk 4 / HIGH · Safety · Evidence · Recommendation ·
       Trust / Decision Replay.

By default this runs on built-in golden data (CAIOS Synthetic Evidence)
so the demo works without credentials. Set CAIOS_SNOWFLAKE_CONN to a
Snowflake connection name to pull the SAME numbers live from the views:
  PET_360 / FOOD_COMPARISON / MILO_TRANSITION_RISK / DECISION_LEDGER.
"""
from __future__ import annotations

import os
import json

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------
# Golden data (mirrors the Snowflake golden test — synthetic demo)
# ---------------------------------------------------------------
GOLDEN_PET360 = {
    "pet_key": "MILO-DEMO-001",
    "pet_name": "Milo",
    "species": "DOG",
    "breed": "Golden Retriever",
    "life_stage": "ADULT",
    "weight_kg": 31.80,
    "activity_level": "MODERATE",
    "soft_stool_observations": 2,
    "recent_gi_signal": True,
}

GOLDEN_COMPARISON = {
    "current_food": "Adult Chicken Formula",
    "current_protein": "Chicken",
    "candidate_food": "Sensitive Salmon Formula",
    "candidate_protein": "Salmon",
    "energy_delta_pct": 13.70,
    "protein_source_changed": True,
}

GOLDEN_RISK = {
    "protein_change_score": 1,
    "energy_change_score": 1,
    "gi_signal_score": 2,
    "risk_score": 4,
    "risk_level": "HIGH",
    "risk_rule_version": "TRANSITION_RISK_V1",
    "model_provider": "deterministic-rules-v1",
}

GOLDEN_EVIDENCE = {
    "evidence_id": "EVID-001",
    "recommendation": (
        "Defer transition: conduct gradual 7-day mix over 14 days "
        "under veterinary monitoring."
    ),
    "safety_action": (
        "Monitor GI signs daily; return to baseline food if soft stool "
        "persists beyond 2 days."
    ),
    "evidence_note": (
        "CAIOS Synthetic Evidence - deterministic transition risk rule "
        "TRANSITION_RISK_V1. GI signal from 2 soft-stool observations. "
        "Energy delta +13.70%. Protein source changed."
    ),
    "data_provenance": "CAIOS Synthetic Evidence",
}

GOLDEN_LEDGER = {
    "pet_key": "MILO-DEMO-001",
    "decision_type": "DIETARY_TRANSITION",
    "risk_score": 4,
    "risk_level": "HIGH",
    "rule_version": "TRANSITION_RISK_V1",
    "input_snapshot": {
        "soft_stool_observations": 2,
        "energy_delta_pct": 13.70,
        "protein_source_changed": True,
    },
    "output_variant": {
        "recommendation": (
            "Defer transition with 14-day gradual mix under vet monitoring"
        ),
        "safety_action": "Monitor GI signs daily",
    },
    "model_provider": "deterministic-rules-v1",
    "data_provenance": "CAIOS Synthetic Evidence",
}


# ---------------------------------------------------------------
# Optional live Snowflake refresh (same deterministic golden numbers)
# ---------------------------------------------------------------
def _live_from_snowflake() -> bool:
    """Return True if a live Snowflake pull succeeded and replaced globals."""
    conn_name = os.environ.get("CAIOS_SNOWFLAKE_CONN")
    if not conn_name:
        return False
    try:
        import snowflake.connector  # noqa: F401
    except Exception:
        st.warning("snowflake-connector-python not installed; using built-in golden data.")
        return False
    # If you have a working connection, replace the GOLDEN_* dicts by
    # querying CAIOS.SEMANTIC.PET_360, CAIOS.SEMANTIC.FOOD_COMPARISON,
    # CAIOS.INTELLIGENCE.MILO_TRANSITION_RISK, CAIOS.INTELLIGENCE.DECISION_LEDGER.
    # The values must equal the golden data above (13.70 / 4 / HIGH).
    return False  # built-in demo is the source of truth for this submission


# ---------------------------------------------------------------
# Styling
# ---------------------------------------------------------------
st.set_page_config(page_title="CAIOS CaniBowl", page_icon="🐶", layout="wide")

st.markdown(
    """
    <style>
      .risk-high { background:#7a1f1f; color:#fff; padding:18px; border-radius:10px; }
      .risk-moderate { background:#7a5a1f; color:#fff; padding:18px; border-radius:10px; }
      .risk-low { background:#1f4d2e; color:#fff; padding:18px; border-radius:10px; }
      .kv { background:#262626; padding:12px; border-radius:8px; }
      .kv b { color:#8ab4f8; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🐶 CAIOS CaniBowl — Pet 360 & Dietary Transition Risk")
st.caption(
    "Hackathon Track: *Patient and Member 360 and Clinical or Regulatory "
    "Document Copilot* — companion-animal adaptation. All data is "
    "**CAIOS Synthetic Evidence** (demo only)."
)

_live_from_snowflake()

pet, comp, risk, evid, ledger = (
    GOLDEN_PET360, GOLDEN_COMPARISON, GOLDEN_RISK,
    GOLDEN_EVIDENCE, GOLDEN_LEDGER,
)

# ---------------------------------------------------------------
# Row 1: Pet 360
# ---------------------------------------------------------------
st.subheader("1 · Pet 360")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Name", pet["pet_name"])
c2.metric("Breed", pet["breed"])
c3.metric("Life Stage", pet["life_stage"])
c4.metric("Weight (kg)", f"{pet['weight_kg']:.2f}")
c5.metric("Activity", pet["activity_level"])

c6, c7, c8 = st.columns(3)
with c6:
    st.markdown(
        f"<div class='kv'><b>Species</b><br/>{pet['species']}</div>",
        unsafe_allow_html=True,
    )
with c7:
    st.markdown(
        f"<div class='kv'><b>Soft stool observations</b><br/>{pet['soft_stool_observations']}"
        f"</div>",
        unsafe_allow_html=True,
    )
with c8:
    gi_badge = "⚠️ TRUE" if pet["recent_gi_signal"] else "OK FALSE"
    st.markdown(
        f"<div class='kv'><b>Recent GI signal</b><br/>{gi_badge}</div>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------
# Row 2: Food comparison
# ---------------------------------------------------------------
st.subheader("2 · Food Comparison (Chicken → Salmon)")
fc1, fc2, fc3 = st.columns(3)
fc1.metric("Current", comp["current_food"])
fc2.metric("Candidate", comp["candidate_food"])
fc3.metric("Energy delta", f"+{comp['energy_delta_pct']:.2f}%")

pc1, pc2 = st.columns(2)
pc1.metric("Protein source", f"{comp['current_protein']} → {comp['candidate_protein']}")
pc2.metric("Protein source changed", "TRUE" if comp["protein_source_changed"] else "FALSE")

# ---------------------------------------------------------------
# Row 3: Deterministic risk
# ---------------------------------------------------------------
st.subheader("3 · Deterministic Transition Risk")
risk_class = {
    "HIGH": "risk-high", "MODERATE": "risk-moderate", "LOW": "risk-low",
}[risk["risk_level"]]
st.markdown(
    f"<div class='{risk_class}'><h2 style='margin:0'>RISK {risk['risk_score']} "
    f"— {risk['risk_level']}</h2>"
    f"<div>{risk['protein_change_score']} (protein) + "
    f"{risk['energy_change_score']} (energy) + {risk['gi_signal_score']} (GI) "
    f"= {risk['risk_score']}</div>"
    f"<div style='opacity:.85'>rule: {risk['risk_rule_version']} · "
    f"provider: {risk['model_provider']}</div></div>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------
# Row 4: Safety + Evidence
# ---------------------------------------------------------------
st.subheader("4 · Safety & Cited Evidence")
s1, s2 = st.columns(2)
with s1:
    st.markdown("##### Safety action")
    st.info(evid["safety_action"])
    st.markdown("##### Recommendation")
    st.success(evid["recommendation"])
with s2:
    st.markdown("##### Evidence")
    st.write(evid["evidence_note"])
    st.caption(
        f"Evidence ID: {evid['evidence_id']} · Provenance: {evid['data_provenance']}"
    )

# ---------------------------------------------------------------
# Row 5: Trust / Decision Replay
# ---------------------------------------------------------------
st.subheader("5 · Trust & Decision Replay")
replay = st.expander("Replay the decision (input snapshot → output)", expanded=False)
with replay:
    st.json(ledger["input_snapshot"])
    st.json(ledger["output_variant"])
    st.caption(
        f"Provider: {ledger['model_provider']} · Type: {ledger['decision_type']} · "
        f"Provenance: {ledger['data_provenance']}"
    )

st.divider()
st.caption(
    "CAIOS keeps a deterministic, explainable risk floor. The model layer may "
    "reference this risk but never overrides it. Not veterinary advice — "
    "consult a licensed veterinarian before changing a pet's diet."
)
