# DrugVLAB — 화면 구조 (IA)

## 메뉴 구조

```
DrugVLAB
├── Portfolio          (프로젝트 운영 대시보드)
├── Workflows          (기존 실행 화면 — 변경 없음)
│   ├── PPI Inhibitor
│   ├── Kinase Inhibitor
│   ├── Drug Response (Preclinical)
│   └── Drug Response (Clinical)
├── Review             (신규)
│   ├── Pending Reviews
│   └── Decision History
├── Library            (기존 — 변경 없음)
├── Data Management    (기존 — 변경 없음)
└── Settings / Admin   (기존 + role 관리 추가)
```

---

## 화면 1 — Portfolio

기존 Dashboard를 대체. 운영 대시보드 역할.

### 표시 항목
- 활성 프로젝트 수 / 최근 실행 요약
- 워크플로우별 COMPLETED / RUNNING / FAILED 현황
- **Pending Review 카운트** (신규) — 결과가 나왔지만 review 미완료인 라이브러리 수
- 최근 decision history 5건 (신규)

### 설계 포인트
- "분석이 끝났다"가 아니라 "검토가 남았다"는 운영 상태를 전면에 표시
- Pending Review → Review 화면으로 바로 이동 가능

---

## 화면 2 — 결과 상세 (기존 화면에 패널 추가)

`DrugResponseClinicalResults`, `DrugResponsePreclinicalResults`, kinase/ppi inhibitor result 화면 공통.

### 추가되는 패널 3개

#### Recommendation Card
```
┌─────────────────────────────────────────┐
│ Compound: ABC-001                        │
│ Predicted Response: HIGH (0.82)          │
│ Confidence: ████████░░ 80%              │
│ Rank: #1 / 47 candidates                │
│ vs. Reference Drug: Imatinib (+12%)     │
└─────────────────────────────────────────┘
```

#### Evidence Panel
```
┌─────────────────────────────────────────┐
│ Mechanism Evidence                       │
│ • Similar known drugs: Dasatinib, ...   │
│ • MoA alignment: BCR-ABL inhibition     │
│ • Top pathways: PI3K/AKT ↓, MAPK ↓    │
│ • Gene interactions: [attention map]    │
│ • Docking score: -9.2 kcal/mol          │
│ • Key interactions: HIS361, ASP381...   │
└─────────────────────────────────────────┘
```

#### Context Panel (Clinical만 해당)
```
┌─────────────────────────────────────────┐
│ Translational Context (THERAPI)          │
│ • Nearest cell lines: K562, KU-812      │
│ • Tissue consistency: 0.91              │
│ • Heterogeneity score: moderate         │
│ • Domain shift risk: LOW                │
│ • Responder subgroup: 68% of cohort     │
└─────────────────────────────────────────┘
```

#### Review Panel (신규 핵심)
```
┌─────────────────────────────────────────┐
│ Review                        [reviewer]│
│  ● Go   ○ Hold   ○ No-Go               │
│                                         │
│  Memo:                                  │
│  [                                    ] │
│                                         │
│  Suggested next experiment:            │
│  [                                    ] │
│                                         │
│  [ Submit Review ]                      │
│─────────────────────────────────────────│
│ Previous: GO — sci@pharma.com           │
│ 2026-05-08  "Pathway evidence strong,   │
│              confirm in xenograft"      │
└─────────────────────────────────────────┘
```
- `reviewer` role이 없는 사용자: read-only (기존 review 이력만 표시)
- `researcher`: review 요청(notify reviewer) 버튼만 표시

---

## 화면 3 — Review (신규)

### 3-1. Pending Reviews

reviewer가 검토해야 할 라이브러리 목록.

```
┌──────────────────────────────────────────────────────┐
│ Pending Reviews                          [ 7 items ] │
├────────────┬──────────────┬──────────┬───────────────┤
│ Library    │ Workflow     │ Round    │ Requested by  │
├────────────┼──────────────┼──────────┼───────────────┤
│ proj-A-001 │ chemgen      │ round_2  │ user@org.com  │
│ proj-B-012 │ drug-resp-cl │ round_1  │ user2@org.com │
└────────────┴──────────────┴──────────┴───────────────┘
```

행 클릭 → 해당 결과 상세 화면으로 이동 (Review Panel 포커스)

### 3-2. Decision History

그룹 내 전체 review 이력.

```
필터: [ All ▼ ] [ GO | HOLD | NO-GO ] [ Workflow ▼ ] [ Date range ]

┌────────────┬──────────┬────────┬────────────┬──────────────┐
│ Library    │ Workflow │ Round  │ Decision   │ Reviewer     │
├────────────┼──────────┼────────┼────────────┼──────────────┤
│ proj-A-001 │ chemgen  │ round_2│ ● GO       │ sci@org.com  │
│ proj-B-012 │ drug-resp│ round_1│ ◐ HOLD     │ lead@org.com │
│ proj-C-007 │ kinase   │ round_1│ ✗ NO-GO    │ sci@org.com  │
└────────────┴──────────┴────────┴────────────┴──────────────┘
```

---

## 화면 4 — Decision Card (Export)

Review 완료 후 생성되는 회의용 artifact.

```
┌─────────────────────────────────────────────────────┐
│ DrugVLAB Decision Card                              │
│ Generated: 2026-05-12  |  Project: proj-A-001       │
├─────────────────────────────────────────────────────┤
│ RECOMMENDATION: GO                                   │
│ Compound: ABC-001  |  Target: BCR-ABL               │
├──────────────────────┬──────────────────────────────┤
│ Predicted Response   │ HIGH (0.82, CI: 0.74–0.89)   │
│ Translational Fit    │ 0.91 (tissue-consistent)      │
│ MoA Evidence         │ BCR-ABL inhibition (strong)   │
│ Similar Known Drug   │ Dasatinib (similarity: 0.87)  │
│ Key Pathway          │ PI3K/AKT ↓, MAPK ↓           │
├──────────────────────┴──────────────────────────────┤
│ Reviewer Memo                                        │
│ "Pathway evidence strong, confirm in xenograft.      │
│  Consider combination with PI3K inhibitor."          │
├─────────────────────────────────────────────────────┤
│ Suggested Next Experiment                            │
│ In vivo xenograft (BCR-ABL+ line), dose: 10mg/kg    │
├─────────────────────────────────────────────────────┤
│ Reviewed by: sci@pharma.com  |  2026-05-08          │
└─────────────────────────────────────────────────────┘
```

Export 형식: JSON (v1), PDF (v2)

---

## Settings / Admin 변경

기존 AdminPage에 **역할 관리** 섹션 추가.

```
User Management
├── 기존: 사용자 목록, 활성화/비활성화
└── 추가: Role 컬럼 (researcher / reviewer / admin)
          [ Grant Reviewer ] / [ Revoke ] 버튼
```
