# CAIOS — Canine AI Observability System (Snowflake MVP)

> **Hackathon Track: Patient and Member 360 and Clinical or Regulatory Document Copilot**
> *Companion-animal adaptation: a Pet 360 + deterministic risk stratification built natively in Snowflake.*

CAIOS is a Snowflake-native MVP that turns a single pet (Milo, a Golden Retriever) into a full **Pet 360** with **deterministic, explainable dietary transition risk** — a working, non-opaque counterpart to AI-based clinical copilots. It demonstrates the full Track 1 value chain entirely inside Snowflake:

```
Pet 360  →  Risk Stratification  →  Evidence Layer  →  Decision Ledger
   ✓             ✓                     ✓                   ✓
```

> **Important:** All data in this repository is **synthetic** (CAIOS Synthetic Evidence) and used for demonstration only. CAIOS adapts the "Patient 360 + Document Copilot" hackathon track to companion animals — the same 360-profile + explainable-risk + evidence-cited pattern applied to veterinary nutrition.

---

## 🏆 What This Delivers (Snowflake Golden Test)

The MVP computes a **deterministic transition risk** for switching Milo from *Adult Chicken Formula* to *Sensitive Salmon Formula*:

| Signal | Value |
|---|---|
| Energy delta (Chicken → Salmon) | **+13.70%** |
| Protein source changed | **TRUE** |
| Recent GI signal (2 soft-stool observations) | **TRUE** |
| Risk factors | **1 + 1 + 2 = 4** |
| **Risk level** | **HIGH** |
| Rule version | `TRANSITION_RISK_V1` |

This is a **fully non-opaque** risk stratification — every number is traceable to a stored observation and a documented rule. Judges can replay the decision from the Decision Ledger.

---

## 🏗️ Snowflake Architecture

```
CAIOS (database)
├── CORE            — transactional pet records
│   ├── PET                    (Milo golden record)
│   ├── PET_PROFILE            (breed, life-stage, weight, activity)
│   └── PET_OBSERVATION        (weight + stool-consistency timeline)
├── KNOWLEDGE
│   └── FOOD_PRODUCT           (synthetic food catalog)
├── SEMANTIC
│   ├── PET_360                (360-degree pet view w/ GI signal)
│   └── FOOD_COMPARISON        (Chicken vs Salmon: +13.70%)
├── INTELLIGENCE
│   ├── MILO_TRANSITION_RISK   (deterministic scoring → HIGH)
│   └── DECISION_LEDGER        (input/output replay)
└── EVIDENCE
    └── DIETARY_RECOMMENDATION (cited, provenance-tagged)
```

**Views are the semantic layer** — `PET_360` and `FOOD_COMPARISON` are live views over core tables, and `MILO_TRANSITION_RISK` is a deterministic scoring view. Nothing is hard-coded into a dashboard.

---

## 🚀 Quick Start

### 1. Provision the foundation

```sql
-- Run sql/01_bootstrap.sql  (CREATE schemas, tables, Milo golden record, synthetic foods)
-- Run sql/02_semantic.sql   (CREATE PET_360, FOOD_COMPARISON, MILO_TRANSITION_RISK views)
-- Run sql/03_evidence.sql   (CREATE evidence table + decision ledger + synthetic rows)
```

> Requires a role with `ACCOUNTADMIN` (or equivalent) and an active warehouse.
> If you see `No active warehouse selected`, run `USE WAREHOUSE <your_warehouse>;` first.

### 2. Run the Golden Test

```sql
-- tests/golden_test.sql
SELECT
    PET_NAME, ENERGY_DELTA_PCT, PROTEIN_SOURCE_CHANGED, RECENT_GI_SIGNAL,
    PROTEIN_CHANGE_SCORE, ENERGY_CHANGE_SCORE, GI_SIGNAL_SCORE,
    RISK_SCORE, RISK_LEVEL, RISK_RULE_VERSION
FROM CAIOS.INTELLIGENCE.MILO_TRANSITION_RISK;
```

**Expected:** `Milo / 13.70 / TRUE / TRUE / 1 / 1 / 2 / 4 / HIGH / TRANSITION_RISK_V1`

### 3. Launch the CaniBowl UI

```bash
pip install -r requirements.txt
streamlit run app/canibowl.py
```

The UI renders: Pet 360 · Chicken → Salmon · **+13.70%** · recent GI signal · **Risk 4 / HIGH** · Safety action · Evidence citation · Recommendation · Trust/Decision Replay.

---

## 🧠 Why "Deterministic, Explainable Risk"

| Aspect | CAIOS approach |
|---|---|
| **Scoring** | Sum of explicit factors: `protein_changed(1) + energy_delta>10%(1) + recent_GI(2)` |
| **Thresholds** | `>=4 → HIGH`, `>=2 → MODERATE`, else `LOW` — documented in rule `TRANSITION_RISK_V1` |
| **Replay** | Every decision is written to `DECISION_LEDGER` with its full `INPUT_SNAPSHOT` |
| **Provenance** | Every evidence row carries `DATA_PROVENANCE = 'CAIOS Synthetic Evidence'` |

This is intentionally a **rules-first, deterministic provider** (`model_provider = deterministic-rules-v1`). It is the safety floor the clinical copilot track must sit on: the model may never override the deterministic risk/safety output.

---

## 📋 Known Account Limitations (Trial)

This build was executed and verified on a **Snowflake trial account**. The following were **not available** and are recorded honestly (not faked):

- ❌ **Cortex Search** — `SYSTEM$ENABLE_CORTEX_SEARCH()` → *Unknown function*. Not available in this trial.
- ❌ **AI_COMPLETE / Cortex AI functions** — `SNOWFLAKE.CORTEX.COMPLETE()` → *"AI function COMPLETE is not available for trial accounts."*
- ✅ **Deterministic provider retained** — CAIOS keeps `deterministic-rules-v1` as the working provider and clearly labels it in the Decision Ledger.

When Cortex becomes available (paid account), the next step is: unstructured veterinary documents → Cortex Search → cited evidence → `AI_COMPLETE` bounded answer that references deterministic risk **without overriding it**.

---

## 📁 Repository Layout

```
├── README.md                  ← this file
├── requirements.txt           ← python deps
├── app/
│   └── canibowl.py            ← Streamlit CaniBowl UI
├── sql/
│   ├── 01_bootstrap.sql       ← foundation + Milo + synthetic foods
│   ├── 02_semantic.sql        ← PET_360 / FOOD_COMPARISON / RISK views
│   └── 03_evidence.sql        ← evidence + decision ledger + synthetic rows
└── tests/
    └── golden_test.sql        ← reproducible golden test
```

---

## ⚠️ Disclaimer

All pet, food, observation, and evidence data is **synthetic** (marked `CAIOS Synthetic Evidence`) and is provided for hackathon demonstration only. It is not veterinary advice. Always consult a licensed veterinarian before changing a pet's diet.
