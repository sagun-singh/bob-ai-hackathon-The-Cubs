# Solution Overview

## What We Built

[We built an AI-powered intelligence tool that automatically reads batches of police FIR text reports. The application categorizes the crime type, extracts key details like names, locations, and methods used, and automatically connects similar cases across different districts to flag repeat offenders, helping officers solve crimes faster.

## How It Works

Explain the core mechanism step by step. A numbered list or simple flow works well here.

1. Upload FIR Batch: Officers upload a batch of unstructured FIR text documents or reports into the system.
2. AI Analysis & Extraction: Bob ingests the text, automatically categorizes the crime type, and extracts key entities like suspects, locations, modus operandi (MO), and victim profiles.
3. Pattern & Repeat Detection: The system compares the new data across all records to uncover hidden connections between cases from different districts and flags repeat-offender signatures
4. Summary & Insights: A station-level crime trend summary table and a highlighted list of repeat offenders are instantly displayed on the dashboard for officers to review.

## Architecture Diagram

> See [`architecture.md`](architecture.md) for the detailed diagram.

Optionally include a simple ASCII or Mermaid diagram here for quick reference.

```
[User] → [Frontend: React] → [API: FastAPI] → [watsonx.ai] → [Dashboard]
                                    ↓
                             [PostgreSQL DB]
```

## Key Design Decisions

| Decision | Rationale |
|---|---|
| [e.g., Used watsonx.ai for anomaly detection] | [e.g., Pre-trained models reduced time-to-value vs. building from scratch] |
| [Decision 2] | [Rationale 2] |
| [Decision 3] | [Rationale 3] |

## IBM Technologies Used

[Explain specifically HOW you used each IBM technology — not just that you used it.]

- **[IBM Tech 1, e.g., watsonx.ai]:** [How it was used — e.g., "Used the `ibm/granite-13b-instruct-v2` model via the Python SDK to classify anomaly types from log text."]
- **[IBM Tech 2]:** [How it was used]
