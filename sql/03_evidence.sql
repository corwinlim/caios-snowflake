-- =========================================================
-- CAIOS Evidence Layer + Decision Ledger
-- All data is CAIOS Synthetic Evidence (demo only)
-- =========================================================

USE ROLE ACCOUNTADMIN;
USE DATABASE CAIOS;
-- USE WAREHOUSE <YOUR_WAREHOUSE>;

-- ---------------------------------------------------------
-- Evidence: cited dietary recommendation
-- ---------------------------------------------------------

CREATE OR REPLACE TABLE CAIOS.EVIDENCE.DIETARY_RECOMMENDATION (
    EVIDENCE_ID VARCHAR,
    PET_KEY VARCHAR,
    CURRENT_FOOD_NAME VARCHAR,
    CANDIDATE_FOOD_NAME VARCHAR,
    RISK_LEVEL VARCHAR,
    RISK_SCORE NUMBER,
    RECOMMENDATION VARCHAR,
    SAFETY_ACTION VARCHAR,
    EVIDENCE_NOTE VARCHAR,
    DATA_PROVENANCE VARCHAR,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

INSERT INTO CAIOS.EVIDENCE.DIETARY_RECOMMENDATION (
    EVIDENCE_ID, PET_KEY, CURRENT_FOOD_NAME, CANDIDATE_FOOD_NAME,
    RISK_LEVEL, RISK_SCORE, RECOMMENDATION, SAFETY_ACTION, EVIDENCE_NOTE, DATA_PROVENANCE
) VALUES (
    'EVID-001', 'MILO-DEMO-001', 'Adult Chicken Formula', 'Sensitive Salmon Formula',
    'HIGH', 4,
    'Defer transition: conduct gradual 7-day mix over 14 days under veterinary monitoring.',
    'Monitor GI signs daily; return to baseline food if soft stool persists beyond 2 days.',
    'CAIOS Synthetic Evidence - deterministic transition risk rule TRANSITION_RISK_V1. '
    'GI signal from 2 soft-stool observations. Energy delta +13.70%. Protein source changed.',
    'CAIOS Synthetic Evidence'
);

-- ---------------------------------------------------------
-- Decision Ledger (replayable decisions)
-- ---------------------------------------------------------

CREATE OR REPLACE TABLE CAIOS.INTELLIGENCE.DECISION_LEDGER (
    LEDGER_ID VARCHAR DEFAULT UUID_STRING(),
    PET_KEY VARCHAR,
    DECISION_TS TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    DECISION_TYPE VARCHAR,
    RISK_SCORE NUMBER,
    RISK_LEVEL VARCHAR,
    RULE_VERSION VARCHAR,
    INPUT_SNAPSHOT VARIANT,
    OUTPUT_VARIANT VARIANT,
    EVIDENCE_REF VARCHAR,
    MODEL_PROVIDER VARCHAR,
    DATA_PROVENANCE VARCHAR
);

-- Note: OBJECT_CONSTRUCT is only valid in a SELECT, not a bare VALUES clause.
INSERT INTO CAIOS.INTELLIGENCE.DECISION_LEDGER (
    PET_KEY, DECISION_TYPE, RISK_SCORE, RISK_LEVEL, RULE_VERSION,
    INPUT_SNAPSHOT, OUTPUT_VARIANT, EVIDENCE_REF, MODEL_PROVIDER, DATA_PROVENANCE
)
SELECT
    'MILO-DEMO-001', 'DIETARY_TRANSITION', 4, 'HIGH', 'TRANSITION_RISK_V1',
    OBJECT_CONSTRUCT(
        'soft_stool_observations', 2,
        'energy_delta_pct', 13.70,
        'protein_source_changed', TRUE
    ),
    OBJECT_CONSTRUCT(
        'recommendation', 'Defer transition with 14-day gradual mix under vet monitoring',
        'safety_action', 'Monitor GI signs daily'
    ),
    'EVID-001',
    'deterministic-rules-v1',
    'CAIOS Synthetic Evidence';

-- ---------------------------------------------------------
-- VERIFY
-- ---------------------------------------------------------

SELECT PET_KEY, DECISION_TYPE, RISK_SCORE, RISK_LEVEL, RULE_VERSION,
       MODEL_PROVIDER, INPUT_SNAPSHOT
FROM CAIOS.INTELLIGENCE.DECISION_LEDGER;

SELECT EVIDENCE_ID, PET_KEY, CURRENT_FOOD_NAME, CANDIDATE_FOOD_NAME,
       RISK_LEVEL, RISK_SCORE, SAFETY_ACTION, DATA_PROVENANCE
FROM CAIOS.EVIDENCE.DIETARY_RECOMMENDATION;
