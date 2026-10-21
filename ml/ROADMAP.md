# Agentis — Hackathon Task Split & Team Roadmap

> **GIFT IFIH YBP Hackathon — Track 1: Agentic AI in Financial Services**  
> **Lead Engineer (YOU + Antigravity Copilot)**: Core ML Ensemble, Bedrock Agents, HITL Gate Orchestration  
> **Teammates (3)**: Specialized modular micro-tasks

---

## 1. Executive Work Split

```
                              ┌─────────────────────────────────────────┐
                              │  YOU (Lead Tech + Copilot)              │
                              │  - ML Spoof Detection Ensemble          │
                              │  - Bedrock Execution & Audit Agents     │
                              │  - HITL Gate & Self-Correction Logic    │
                              └────────────────────┬────────────────────┘
                                                   │
         ┌─────────────────────────────────────────┼─────────────────────────────────────────┐
         ▼                                         ▼                                         ▼
┌──────────────────────────┐             ┌──────────────────────────┐             ┌──────────────────────────┐
│ TEAMMATE 2               │             │ TEAMMATE 3               │             │ TEAMMATE 4               │
│ Backend Data & DB Helper │             │ Frontend UI Shell        │             │ Audio & Docs Lead        │
│ Task: Synthetic CSV & DB │             │ Task: Dashboard React    │             │ Task: 3 Audio Clips &    │
│ Schemas                  │             │ Components               │             │ 1-Pager PDF              │
└──────────────────────────┘             └──────────────────────────┘             └──────────────────────────┘
```

---

## 2. Bite-Sized Task Cards to Assign to Teammates

Copy and paste these exact task blocks directly to your teammates so they can work independently while we build the core engine!

---

### 📋 TEAMMATE 2: Backend Synthetic Data & DB Helper
**Goal**: Create the raw synthetic treasury dataset CSV and the database schema files.

* **Task 2.1 — Synthetic Treasury Exposure CSV Generator**:
  - Write a Python script `backend/data_gen/generate_treasury_data.py` using `Faker` and `pandas`.
  - Generate a 30-day time-series of currency exposures across USD, EUR, GBP, JPY, and INR for 5 synthetic multinational corporate entities.
  - Include columns: `Timestamp`, `Entity_ID`, `Currency_Pair`, `Exposure_Amount`, `Volatility_Index`, `Risk_Level` (`LOW`, `MEDIUM`, `HIGH`).
  - Add 3 deliberate risk-threshold spikes (Exposures $> \$500,000$ USD equivalent) to trigger the HITL guardrail.

* **Task 2.2 — DynamoDB Schema & Seed Data JSON**:
  - Create `backend/db/schemas.json` defining 3 tables: `TreasuryBalances`, `TransferCases`, and `AuditLogs`.
  - Provide sample JSON seed objects for testing.

---

### 🎨 TEAMMATE 3: Frontend & Dashboard UI Helper
**Goal**: Build the React UI layout shell and visual components.

* **Task 3.1 — React Dashboard Shell**:
  - Set up a clean React dashboard (using Tailwind CSS or standard CSS) under `frontend/`.
  - Create 4 visual cards/panels:
    1. **Treasury Exposure Overview**: Cards showing current multi-currency holdings & active risk flags.
    2. **HITL Pending Verification Modal**: Modal popup showing pending transfer ($> \$500,000$) with a "Play Sign-off Audio" button and "Initiate Voice Scan" button.
    3. **Spoof Detection Score Gauge**: Visual gauge showing Ensemble Score (0.0 to 1.0) and Self-Correction Status (`PENDING`, `METADATA_RECHECKED`, `VERIFIED_HUMAN`, `SPOOF_DETECTED`).
    4. **DPDP Compliance Audit Log Table**: Table displaying execution logs with timestamps, anonymized caller hashes, confidence scores, and action taken (`RELEASED` / `BLOCKED`).

---

### 📄 TEAMMATE 4: Audio Samples, Regulatory & Narrative Lead
**Goal**: Produce the 3 demo audio clips and write the business/regulatory deliverables.

* **Task 4.1 — Demo Audio Set Creation**:
  - Source/record 3 short WAV audio files (~5-10 seconds each) of a CFO approving a transfer: *"This is CFO Sarah Jenkins approving wire transfer TXN-99482 for 750,000 US Dollars."*
    - File 1: `real_signoff_01.wav` (authentic human voice).
    - File 2: `cloned_signoff_deepfake.wav` (ElevenLabs / TTS generated fake of the same voice).
    - File 3: `ambiguous_signoff_noise.wav` (real voice with heavy background static / room echo to trigger self-correction re-check).
  - Save these files in `ml_engine/dataset/samples/`.

* **Task 4.2 — Hackathon 1-Pager & Regulatory Pathway**:
  - Write `docs/1_pager_agentis.md` following the required 8-section hackathon template.
  - Write `docs/regulatory_pathway_dpdp_gift.md` explaining how Agentis complies with India's DPDP Act 2023 (no raw audio stored, ephemeral processing, cryptographic metadata hashing) and GIFT City IFSC treasury regulations.

---

## 3. Major Core Tasks (YOU + Antigravity Copilot)

We will build the primary technical engine step-by-step:

1. **`ml_engine/`**: The LCNN + Wav2Vec2 + Librosa Prosody Spoof Detection Ensemble & SageMaker inference contract.
2. **`backend/agents/`**: Bedrock Treasury Execution Agent (monitors exposure, proposes hedges, pauses at HITL gate) & Voice Verification & Audit Agent (scores call, executes self-correction metadata re-check on ambiguous scores $0.35 - 0.65$, outputs PASS/BLOCK).
3. **`backend/lambda_handlers/`**: The HITL Gate Orchestrator glue linking exposure alerts, voice scoring, self-correction, DynamoDB audit logging, and fund release/block.
4. **`README.md`**: Master setup guide, architecture flowcharts, and technical "Mocked vs. Real" disclosure.
