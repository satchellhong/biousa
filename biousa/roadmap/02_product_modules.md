# DrugVLAB — 핵심 모듈 3개

## 제품 구조 3계층

```
┌─────────────────────────────────────────────────────────┐
│  Workflow Layer  │  프로젝트 · 실행 · 리뷰 · export · audit  │
│  (이미 구축됨 + Review 추가 필요)                           │
├─────────────────────────────────────────────────────────┤
│  Translation Layer  │  THERAPI: alignment · heterogeneity  │
│  "이 결과가 우리 샘플에도 맞나"                              │
├─────────────────────────────────────────────────────────┤
│  Evidence Layer  │  CSG2A: MoA · pathway · perturbation  │
│  "왜 이 후보가 올라왔나"                                    │
└─────────────────────────────────────────────────────────┘
```

---

## Module 1 — Cohort Twin

**"이 샘플을 어떤 biological context로 봐야 하나"**

THERAPI 기반. 내부 환자·오가노이드·사내 샘플을 preclinical reference(GDSC, CCLE 등)와 공통 embedding space 위에 정렬.

### 제공하는 것
- 샘플별 nearest preclinical analog 집합 (attention-weighted cell-line mixture)
- Tumor heterogeneity score
- Tissue consistency 지표
- Domain shift risk (내부 샘플이 reference distribution에서 얼마나 벗어나 있는가)
- External cohort generalization 신뢰도

### 사용자 관점의 가치
> "우리 환자 샘플이 GDSC 기준으로 어떤 cell line과 가장 가깝고, 그 cell line에서 어떤 약물이 효과적이었나"를 즉시 확인할 수 있다.

### 연결되는 워크플로우
`workflow_chemresponse_clinical_round1` (THERAPI 모델)

---

## Module 2 — Response Explorer

**"왜 이 약물이 우선순위인가"**

THERAPI + CSG2A 결합. 후보 약물의 반응 가능성을 샘플/코호트 단위로 순위화하고, responder subgroup signal을 제시.

### 제공하는 것
- 약물별 predicted response score + confidence band
- Responder likelihood (고반응군/저반응군 stratification)
- Subgroup effect (heterogeneous sample 내 partial responder 탐지)
- 비교 약물 대비 상대 순위
- Preclinical-to-clinical translation fit score

### 사용자 관점의 가치
> "이 후보 5개 중 우리 코호트에서 가장 가능성 높은 순서와, 그 근거가 얼마나 강한지를 한 화면에서 본다."

### 연결되는 워크플로우
`workflow_chemresponse_clinical_round1` (THERAPI)
`workflow_chemresponse_preclinical_round1` (CSG2A + THERAPI)
`workflow_chemgen_kinase_round1`, `workflow_chemgen_round1` (생성된 후보의 ranking)

---

## Module 3 — Mechanism Lens

**"이 결과를 과학적으로 어떻게 설명할 수 있나"**

CSG2A 기반. Chemical-induced gene-gene perturbation과 pathway reversal을 약물 MoA와 정렬하여 설명 근거를 제공.

### 제공하는 것
- Gene-gene attention map (조건별 interaction 변화)
- Pathway perturbation score (알려진 pathway 대비 활성화/억제 정도)
- MoA similarity (known drug와의 mechanism alignment)
- Similar known drugs (같은 MoA 계열 reference 약물 목록)
- Interaction profiling (PLIP 기반 docking 상호작용 summary)

### 사용자 관점의 가치
> "이 후보가 왜 효과적일 것으로 예측되는지를, 기존 알려진 약물과의 MoA 유사성과 pathway 근거로 설명할 수 있다."

### 연결되는 워크플로우
`workflow_chemresponse_preclinical_round1` (CSG2A)
`workflow_chemgen_round1`, `workflow_chemgen_kinase_round1` (docking/PLIP/affinity)

---

## 모듈 간 연결 흐름

```
[내부 샘플 업로드]
       ↓
[Cohort Twin] ── tissue mapping, nearest analog, heterogeneity
       ↓
[Response Explorer] ── ranked candidates, responder stratification
       ↓
[Mechanism Lens] ── pathway evidence, MoA alignment, perturbation
       ↓
[Review Panel] ── go / hold / no-go + memo + decision history
       ↓
[Export] ── review packet (JSON / PDF)
```

---

## 상품 패키지 매핑

| 패키지 | 포함 모듈 | 대상 팀 |
|---|---|---|
| **Explorer** | Cohort Twin + Response Explorer | Discovery 팀 |
| **Translator** | 전체 3모듈 | Translational science 팀 |
| **Private Runtime** | 전체 + 고객 환경 배포 + RBAC + audit log | IT/보안 요건이 있는 기업 |
| **Report Generator** | Review Panel + Export (JSON/PDF) | 프로젝트 리더, 의사결정자 |
