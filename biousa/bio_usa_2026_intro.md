# DrugVLAB
## BIO International Convention 2026 | Meeting Material

---

## Slide 1 — Who We Are

**DrugVLAB** is an AI-powered drug discovery platform built for pharmaceutical, biotech, and clinical research teams.

From candidate generation to patient-level response prediction — the full preclinical and translational drug development workflow on a single platform.

---

## Slide 2 — The Gap We Close

Drug development fails most often at translation — when a promising preclinical result doesn't hold up in patients.

```mermaid
flowchart LR
    A["Preclinical\n(Cell lines, animal models)"] -->|"❌ 90%+ failure rate\nat clinical translation"| B["Clinical\n(Patient trials)"]
    style A fill:#fef9c3,stroke:#ca8a04
    style B fill:#fee2e2,stroke:#dc2626
```

The two sides speak different biological languages. Most AI tools are trained on one side and applied blindly to the other.

DrugVLAB bridges them with models specifically designed for the preclinical-to-clinical translation problem.

---

## Slide 3 — Four Capabilities, One Platform

```mermaid
flowchart TD
    A["🎯 Target Protein\nor Compound Library"] --> B["Candidate Generation\nPPI / Kinase Inhibitors"]
    B --> C["In Silico Validation\nDocking · Selectivity · Affinity Ranking"]
    C --> D["Preclinical Response\nCell-line drug response + Mechanism evidence"]
    D --> E["Patient-Level Response\nPer-patient prediction from tumor gene expression"]

    style A fill:#f0fdf4,stroke:#16a34a
    style B fill:#eff6ff,stroke:#3b82f6
    style C fill:#eff6ff,stroke:#3b82f6
    style D fill:#faf5ff,stroke:#9333ea
    style E fill:#fff7ed,stroke:#ea580c
```

All four run on the same platform — same interface, same secure environment, same result management.

---

## Slide 4 — Capability 1 & 2: Candidate Generation

### From protein target to ranked compound shortlist

Starting from a protein target, DrugVLAB generates novel small molecule candidates using AI, then filters and ranks them through a full in silico validation pipeline.

```mermaid
flowchart LR
    A["Protein Target\n(sequence + binding site)"] --> B["AI Molecule\nGeneration"]
    B --> C["Drug-likeness\nFilter\n(ADME, Lipinski)"]
    C --> D["Docking\n(binding pose\nsimulation)"]
    D --> E["Interaction\nProfiling\n(which residues\nbind)"]
    E --> F["Affinity\nPrediction\n(binding strength)"]
    F --> G["Ranked\nCandidate List"]

    style A fill:#f0fdf4,stroke:#16a34a
    style G fill:#dcfce7,stroke:#16a34a
```

**For kinase targets:** The pipeline includes an additional selectivity screen — candidates are also tested against off-target kinases, so the final shortlist is ranked by both potency *and* selectivity.

**What you receive:**
- Ranked candidate list with predicted binding affinity
- Residue-level interaction details (which amino acids each compound contacts)
- Downloadable compound files for synthesis or wet-lab follow-up

---

## Slide 5 — Capability 3: Preclinical Drug Response

### Predicting which cancer cell lines respond — and why

For any candidate compound, DrugVLAB predicts how sensitive or resistant each cancer cell line is, and explains the mechanism behind the prediction.

```mermaid
flowchart LR
    A["Compound\n(chemical structure)"] --> B["AI Model\n(CSG2A)"]
    B --> C["Cell-line\nSensitivity Panel\n(GDSC reference)"]
    B --> D["Pathway\nPerturbation\n(which pathways\nare disrupted)"]
    B --> E["Similar Known\nDrugs\n(mechanistic\nanalogues)"]

    style A fill:#faf5ff,stroke:#9333ea
    style C fill:#f3e8ff,stroke:#9333ea
    style D fill:#f3e8ff,stroke:#9333ea
    style E fill:#f3e8ff,stroke:#9333ea
```

**Why mechanism matters for your team:**
- "Is this compound acting through the same pathway as drug X?" → answered
- "Which tumor types are most likely sensitive?" → answered
- "What biological process is being disrupted?" → answered

This is not a black-box score. Every prediction comes with biological context.

---

## Slide 6 — Capability 4: Patient-Level Drug Response

### The translational leap — from cell lines to individual patients

This is DrugVLAB's most differentiated capability.

**The problem with standard approaches:**

Most response prediction models are trained on cancer cell lines and applied directly to patient samples. This ignores two fundamental differences:

1. A patient tumor is not a single cell line — it is a mixture of different cell populations with varying drug sensitivities
2. The biological environment of a patient tumor is different from a culture dish

**How DrugVLAB handles this:**

```mermaid
flowchart TD
    A["Patient tumor biopsy\n(gene expression profile)"] --> B["Match to reference\ncell-line panel\n(weighted mixture)"]
    B --> C["Predict response\nfor this specific\npatient profile"]
    C --> D["Classify as\nResponder or\nNon-Responder"]
    D --> E["Assign confidence\nbased on\nmodel agreement"]

    style A fill:#fff7ed,stroke:#ea580c
    style D fill:#dcfce7,stroke:#16a34a
    style E fill:#fef9c3,stroke:#ca8a04
```

The model does not assume a patient looks like any single cell line. It finds the *combination* of cell-line profiles that best matches the patient's tumor biology, and predicts response from that matched context.

**Input required:** Tumor gene expression data (RNA sequencing, ~978 genes)
**Output:** Response probability per patient, with confidence rating

---

## Slide 7 — The Translation Gap — Solved by Design

DrugVLAB includes a second patient-level model (PertDA) that explicitly addresses the preclinical-to-clinical gap through a technique called domain adaptation.

**The core insight:**

```mermaid
flowchart LR
    subgraph Preclinical["Preclinical Data (GDSC)"]
        A["Cell-line drug\nresponse profiles"]
    end
    subgraph Clinical["Clinical Data (TCGA)"]
        B["Patient tumor\ngene expression"]
    end
    subgraph Gap["The Translation Gap"]
        C["Different biological\nenvironments\nDifferent noise patterns\nDifferent scale"]
    end

    Preclinical -->|"Training"| Gap
    Gap -->|"Most models ignore this"| Clinical

    style Gap fill:#fee2e2,stroke:#dc2626
    style Preclinical fill:#eff6ff,stroke:#3b82f6
    style Clinical fill:#fff7ed,stroke:#ea580c
```

PertDA trains the model to *recognize and correct* this gap during learning — not to ignore it.

**Validated result:** AUROC 0.757 on independent TCGA patient cohort (10-model ensemble)

AUROC 0.757 means: if you randomly pick one responder and one non-responder from the cohort, the model correctly identifies which is which 75.7% of the time.

---

## Slide 8 — Two-Model Confidence Framework

Running both patient-response models on the same cohort produces a stratified confidence structure:

```mermaid
quadrantChart
    title Patient Stratification by Model Agreement
    x-axis "THERAPI: Non-Responder" --> "THERAPI: Responder"
    y-axis "PertDA: Non-Responder" --> "PertDA: Responder"
    quadrant-1 "Tier 1: High Confidence Responder"
    quadrant-2 "Tier 3: Review Required"
    quadrant-3 "Tier 2: High Confidence Non-Responder"
    quadrant-4 "Tier 3: Review Required"
```

| Tier | What it means | Recommended action |
|---|---|---|
| **Tier 1** | Both models agree: Responder | Prioritize for trial enrollment |
| **Tier 2** | Both models agree: Non-Responder | Deprioritize |
| **Tier 3** | Models disagree | Collect additional biomarker data before deciding |

**Why two models:** A single model's threshold is arbitrary. Agreement between two models with fundamentally different architectures is a meaningful signal.

---

## Slide 9 — Deployment Options

```mermaid
flowchart LR
    subgraph Hosted["☁️ Hosted SaaS"]
        H1["AigenDrug-managed\nAWS infrastructure"]
        H2["Per-customer\nisolated environment"]
        H3["Ready to use\nimmediately"]
    end

    subgraph Private["🏢 Private Runtime"]
        P1["Deployed into\nyour AWS account"]
        P2["Data never leaves\nyour perimeter"]
        P3["Full access control\nand audit logs"]
    end

    User["Research Team"] -->|"Fast start\nearly validation"| Hosted
    User -->|"Regulatory requirements\nhighly sensitive data"| Private
```

| | **Hosted SaaS** | **Private Runtime** |
|---|---|---|
| Data location | AigenDrug AWS (per-customer isolated) | Your AWS account |
| Time to start | Immediate | Days (Terraform automated) |
| Best for | Early validation, smaller teams | Regulated data, clinical use, enterprise |
| Support | Email | Dedicated CSM + SLA |

---

## Slide 10 — Who Uses DrugVLAB

```mermaid
flowchart LR
    A["Medicinal Chemist"] -->|"Generates and\nranks candidates"| P["DrugVLAB\nPlatform"]
    B["Pharmacologist"] -->|"Predicts cell-line\nresponse + mechanism"| P
    C["Translational\nScientist"] -->|"Predicts patient-level\nresponse + cohort fit"| P
    D["Clinical\nTeam Lead"] -->|"Reviews evidence,\nmakes go/hold decision"| P

    style P fill:#eff6ff,stroke:#3b82f6
    style A fill:#f0fdf4,stroke:#16a34a
    style B fill:#f0fdf4,stroke:#16a34a
    style C fill:#faf5ff,stroke:#9333ea
    style D fill:#fff7ed,stroke:#ea580c
```

Each role interacts with the results most relevant to their decision. One platform serves the full drug development team.

---

## Slide 11 — Current Platform Status

```mermaid
gantt
    title Workflows — Operational Status (June 2026)
    dateFormat YYYY-MM
    section Molecule Generation
    PPI Inhibitor Generation       :done, 2025-03, 2026-06
    Kinase Inhibitor Generation    :done, 2025-05, 2026-06
    section Drug Response
    Preclinical Response (CSG2A)   :done, 2025-06, 2026-06
    Patient-Level Response (THERAPI + PertDA) :done, 2025-09, 2026-06
```

All four workflows are **fully operational** on the live platform today.
AWS security certification (Foundational Technical Review) in progress.

---

## Slide 12 — Partnership Opportunities

We are at BIO USA 2026 looking for three types of collaboration:

**1. Pilot Programs**
Bring a cohort of patient samples and a candidate compound. We run patient-level response prediction together and walk through the results. No commitment required.

**2. Co-development Partners**
Oncology-focused biotech or pharma teams with proprietary translational datasets interested in fine-tuning models on their specific tumor types or indications.

**3. Commercial Deployment**
Deploying DrugVLAB inside your AWS environment with full data isolation, dedicated support, and annual licensing.

---

## Slide 13 — Contact

**AigenDrug**

[Contact information]

We are available for 1:1 meetings throughout BIO USA 2026.
Bring your use case — we will show you the platform live.

---

*DrugVLAB — Fully operational as of June 2026*
