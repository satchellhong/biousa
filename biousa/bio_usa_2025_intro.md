# DrugVLAB — BIO USA 2025 Meeting Deck

> **현재 배포 및 운영 중인 플랫폼 기준** (2025년 5월)  
> 미구현 기능은 포함하지 않음

---

## Slide 1 — Title

**DrugVLAB**  
*Private AI Platform for Drug Discovery & Translational Drug Response Prediction*

AigenDrug  
BIO International Convention 2025

---

## Slide 2 — The Problem We Solve

Three problems that kill R&D productivity — and that most AI tools can't address together:

| Problem | Why existing tools fall short |
|---|---|
| **Preclinical → clinical translation failure** | Models trained on cell lines don't transfer to patients. Tissue context and tumor heterogeneity are ignored. |
| **Cohort-level prediction misses who responds** | Average response rates don't tell you which patients to enroll or prioritize. |
| **Proprietary data can't leave the firewall** | External AI APIs require data upload. That's a non-starter for most pharma and hospital teams. |

DrugVLAB runs **inside your environment**. It addresses all three.

---

## Slide 3 — What DrugVLAB Delivers Today

Four fully operational workflows on a single platform:

### 1. PPI Inhibitor Generation
Generate de novo small molecule candidates targeting protein-protein interaction interfaces.

**Input:** Target protein sequence + PPI binding site  
**Output:** Ranked candidate library with docking scores, interaction profiles, affinity predictions

### 2. Kinase Inhibitor Generation
Generate kinase-targeted candidates with selectivity filtering built in.

**Input:** Target kinase + (optional) known binder scaffold  
**Output:** Ranked candidates with off-target docking — selectivity-aware shortlist

### 3. Preclinical Drug Response Prediction
Predict cell-line drug response with mechanism and pathway evidence.

**Input:** Drug SMILES  
**Output:** lnIC50 prediction across cell-line panel, pathway perturbation scores, MoA similarity to known drugs

### 4. Patient-Level Drug Response Prediction
Predict individual patient response probability from tumor gene expression.

**Input:** Patient GEX (bulk RNA-seq, ~978 genes) + Drug SMILES  
**Output:** Per-patient response probability, responder/non-responder classification, ensemble confidence

---

## Slide 4 — Platform Overview

```
┌──────────────────────────────────────────────────────────┐
│                 Customer Environment                      │
│         (AWS VPC  or  Customer-Managed Cloud)            │
│                                                           │
│   Browser UI (React)  <->  REST API (Django)             │
│                                |                          │
│            AWS Batch  (GPU compute, Nextflow)            │
│                                |                          │
│        EFS (model files)   DynamoDB   S3 (I/O)           │
│                                |                          │
│   Cognito (auth)   KMS   CloudTrail   GuardDuty           │
│                                                           │
│              ^ Patient data never leaves here             │
└──────────────────────────────────────────────────────────┘
```

**Infrastructure highlights:**
- Full Terraform IaC — deployable to any AWS account in days
- AWS Batch for GPU workloads (g5 class instances, CUDA 12.2)
- Cognito-based authentication with role-based access control
- CloudTrail audit trail + GuardDuty threat detection
- AWS FTR (Foundational Technical Review) in progress

---

## Slide 5 — Molecule Generation Pipelines

### PPI Inhibitor Generation

```
Pharmacophore Extraction (binding site analysis)
        |
Molecule Generation
  · Hot2Mol  — hotspot-guided de novo generation
  · Mfrag    — fragment-based generation from assay data
        |
Drug-likeness Filtering  (Lipinski + ADME thresholds)
        |
Docking  (AutoDock Vina)
        |
Interaction Profiling  (PLIP — residue-level binding analysis)
        |
Affinity Prediction  (MixingDTA + CheapNet ensemble)
        |
Ranked Candidate List  ->  Download (SDF, CSV)
```

### Kinase Inhibitor Generation

Same pipeline as PPI, with two additions:
- **Off-target docking**: candidates docked against selectivity panel
- **Off-target affinity filtering**: MixingDTA applied to off-targets; compounds with off-target binding above threshold removed before final ranking

**Result:** Shortlist that accounts for selectivity, not just potency.

---

## Slide 6 — Preclinical Drug Response: CSG2A

### What CSG2A computes

CSG2A learns **chemical-induced gene-gene interaction patterns** conditioned on drug presence.

For any input SMILES:
- Predicts lnIC50 across the GDSC cell-line panel
- Identifies which genes interact differently under drug treatment
- Maps those interactions to pathway perturbation scores
- Compares compound against known drugs by mechanism similarity

**Platform delivers:**
- Drug score ranking (sensitive vs. resistant cell lines)
- lnIC50 distribution with user-adjustable sensitivity cutoff
- Top perturbed pathways per compound
- Similar known drugs by MoA alignment

**UI features live today:**
- Ranked drug score table (filterable by pathway, target, score range)
- lnIC50 histogram with interactive cutoff slider
- Cell-line sensitivity breakdown by tissue and cancer type
- Downloadable result CSVs

---

## Slide 7 — Patient-Level Drug Response: THERAPI

### Bridging cell lines to patients

**The core problem:** Cell-line models ignore that patient tumors are heterogeneous — a single tumor contains cells resembling multiple cell-line types simultaneously.

**THERAPI's approach:**  
Each patient tumor is represented as an **attention-weighted mixture of reference cell lines**, preserving:
- Tissue context (same drug, different tissue → different response)
- Intra-tumor heterogeneity (mixture weights reflect subclonal composition)
- Shared embedding with preclinical reference data

**Training:** GDSC cell-line drug response → **Validation: TCGA patient cohort**

**Input:** Patient GEX CSV (978 gene symbols, log2(TPM+1) scale) + Drug SMILES

**Output per sample:**
```
Sample ID:         TCGA-A2-A3XS
Response prob:     0.78
Ensemble votes:    5/5  (CV1-CV5 all: Responder)
Classification:    Responder
Confidence:        HIGH
```

**Input QC — automatic, before inference runs:**
```
Gene match ratio:  0.99  ->  PASS
Matched:           974 / 978 genes
Missing:           4 genes (listed)
Extra:             12 genes (ignored)
```
Run is blocked if match ratio falls below threshold — preventing silent inference on bad input.

---

## Slide 8 — Patient-Level Drug Response: PertDA

### THERAPI x CSG2A x Domain Adaptation

**PertDA** is the next-generation patient response model, combining three components:

| Component | What it adds |
|---|---|
| THERAPI architecture | Patient GEX encoder + attention-weighted cell-line mixture |
| CSG2A integration | Drug perturbation signal: how *this drug* changes *this patient's* gene expression |
| Domain Adaptation (adversarial) | Explicit GDSC->TCGA distribution alignment during training |

**Inference path:**
```
Patient GEX  ->  raw GEX encoder (VAE)          --|
Drug SMILES  ->  GCN drug branch                  |
Patient GEX  ->  CSG2A -> perturbed GEX latent    |--> response probability
                        -> compound latent         |
Domain Adaptation (GDSC <-> TCGA, adversarial)  --|
```

**Why domain adaptation matters:**

Models trained on cell lines systematically over- or under-predict patient response because the two data distributions differ in batch effects, cellularity, and transcriptional noise. PertDA trains an adversarial discriminator to make the cell-state encoder domain-invariant — the prediction head sees patient and cell-line states as the same distribution.

**Validated on TCGA:**
```
AUROC:       0.757
Std dev:     0.032
Checkpoints: 10-fold ensemble
```

---

## Slide 9 — Two-Model Consensus Stratification

Running THERAPI and PertDA on the same cohort enables a tiered confidence framework:

```
                         PertDA
                    Responder | Non-Responder
                  ------------|--------------
THERAPI Responder |  Tier 1  |   Tier 3     |
                  | (Highest  |  (Review)    |
                  | confidence|              |
                  |-----------|--------------|
THERAPI Non-Resp  |  Tier 3  |   Tier 2     |
                  |  (Review) | (Confirmed   |
                  |           |  Non-Resp)   |
                  |-----------|--------------|
```

| Tier | Meaning | Suggested action |
|---|---|---|
| **Tier 1** — Both Responder | Consensus Responder | Prioritize for enrollment / next experiment |
| **Tier 2** — Both Non-Responder | Consensus Non-Responder | Deprioritize |
| **Tier 3** — Discordant | Model disagreement | Flag for biomarker review before decision |

No single arbitrary threshold. Two independent models with different architectures must agree before a sample is high-confidence.

---

## Slide 10 — Platform Operations

### What a user session looks like

**Molecule generation run:**
1. Create library → select workflow (PPI / Kinase)
2. Upload protein / input parameters via UI
3. Submit → AWS Batch job queued and started
4. Results appear in dashboard (RUNNING → COMPLETED)
5. Open result viewer: ranked table, filter by score / pathway / target
6. Download ligand SDF files, summary CSV

**Drug response run:**
1. Create library → select workflow (Preclinical / Clinical)
2. Upload input CSV (SMILES + GEX path)
3. Validation report shown before run starts — gene coverage confirmed
4. Submit → GPU inference job on AWS Batch
5. Results: per-sample prediction table, distribution plot, sensitivity profile
6. AI assistant on results page answers natural-language questions about the output

**Credit metering:**
- Balance visible in dashboard at all times
- Each run consumes credits based on GPU instance type × runtime
- Admin view: per-user usage history, balance adjustment
- Full ledger queryable via Athena (Parquet archive)

---

## Slide 11 — Security & Infrastructure

| Area | Implementation |
|---|---|
| **Deployment** | Customer AWS VPC or AigenDrug-hosted |
| **Data residency** | All patient and compound data stays within deployment boundary |
| **Authentication** | AWS Cognito, JWT-based |
| **Authorization** | Role-based (researcher / admin); group-scoped data access |
| **Encryption** | KMS for secrets; HTTPS/TLS for all traffic; EFS encryption at rest |
| **Audit** | CloudTrail (all API calls), GuardDuty (threat detection), activity DynamoDB log |
| **Infrastructure** | Terraform IaC — all modules version-controlled and reproducible |
| **Compliance posture** | AWS FTR in progress; WAF on ALB; VPC-isolated compute |

---

## Slide 12 — Target Users

| Role | Primary workflow | What they get |
|---|---|---|
| **Computational chemist** | PPI / Kinase Inhibitor | Ranked candidate library with docking + affinity + interaction detail |
| **Pharmacologist** | Preclinical Drug Response | Cell-line panel predictions, pathway perturbation, MoA similarity |
| **Translational scientist** | Patient-Level Response | Per-patient prediction, cohort stratification, domain-alignment confidence |
| **IT / Compliance** | Platform admin | VPC-isolated deployment, audit logs, role management |

---

## Slide 13 — Packages

| | **Explorer** | **Translator** | **Private Runtime** |
|---|---|---|---|
| PPI / Kinase generation | Yes | Yes | Yes |
| Preclinical response (CSG2A) | Yes | Yes | Yes |
| Patient-level response (THERAPI + PertDA) | No | Yes | Yes |
| Deployment | Hosted SaaS | Hosted SaaS | Customer AWS VPC |
| Data egress policy | Shared infra | Shared infra | No-egress, isolated |
| Audit log + RBAC | Standard | Standard | Full + custom policy |
| Support | Email | Email + call | Dedicated CSM + SLA |

Pricing: platform subscription + credit consumption per run.  
Private Runtime: annual license + one-time deployment fee.

---

## Slide 14 — Next Steps

**We offer:**

- **Live platform demo** — walk through an actual run on hosted environment
- **Pilot program** — bring your cohort GEX data + compound list; we run patient-level prediction and walk through results together
- **Private Runtime PoC** — deploy to your AWS account; your team runs workflows on your data, never leaving your VPC

**Contact:** [contact info]

---

*Platform status: fully deployed and operational, May 2025*  
*AWS FTR in progress*
