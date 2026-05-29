# 환자 수준 약물 반응성 예측 — 세일즈 가이드

## 한 줄 세일즈 메시지

> **환자 조직의 유전자 발현 프로파일만으로, 약물별 반응 가능성을 환자 개인 단위로 예측합니다.**  
> 전임상(cell-line)과 임상(환자) 간 도메인 갭을 Domain Adaptation으로 명시적으로 좁혔으며,  
> 약물의 perturbation 효과까지 통합한 예측을 고객 환경에서 실행합니다.

---

## 고객이 지금 겪는 문제

| 문제 | 고객의 말 |
|---|---|
| 전임상 모델과 환자 간 gap | "cell-line에서 잘 되던 약이 임상에서 안 된다" |
| 코호트 단위 판단의 한계 | "평균 반응률 60%인데, 누가 반응하는지를 모른다" |
| 반응 예측 근거 부재 | "왜 이 환자가 responder일 것이라고 판단해야 하는가" |
| 데이터 반출 불가 | "환자 데이터를 외부 서비스에 올릴 수 없다" |

---

## DrugVLAB이 제공하는 것

### 입력
```
환자 샘플 유전자 발현 프로파일 (bulk RNA-seq 기반, ~1,000개 유전자)
+ 평가 대상 약물 SMILES
```

### 출력 (환자 1명 기준)
```
- 반응 확률: 0.78 (78%)
- 반응군 여부: Responder ✓
- 앙상블 투표: 5/5 모델 반응군 판정 (CV1~CV5)
- 예측 안정성: HIGH (투표 일치율 100%)
- 입력 데이터 검증: PASS (matched 987/1000 genes, match_ratio 0.99)
```

### 코호트 단위 요약
```
- 전체 샘플 수: 48명
- Responder: 31명 (64.6%)
- Non-Responder: 17명 (35.4%)
- 고신뢰 Responder (binaryMean ≥ 0.8): 19명
- 경계 구간 (0.4~0.6): 6명 → 추가 검토 필요
```

---

## 기술 근거 (세일즈 대화용)

### THERAPI 모델이 다른 이유

일반적인 약물 반응 예측 모델은 cell-line 데이터로만 학습한다. 이 경우 환자 종양의 이질성(heterogeneity)과 tissue context를 무시하게 된다.

THERAPI는 환자 샘플을 "여러 cell-line의 attention-weighted mixture"로 표현한다. 즉 환자 종양이 어떤 전임상 reference들과 유사한지를 가중 결합해 shared embedding space 위에 정렬한다. 이 덕분에:

- **Tissue context 보존**: 동일 약물도 tissue에 따라 다른 반응 패턴을 반영
- **Heterogeneity 처리**: 단일 cell-line 매칭이 아닌 mixture 표현으로 종양 내 이질성을 다룸
- **외부 코호트 일반화**: GDSC 학습 → TCGA 예측 검증 완료

### 앙상블 설계의 의미

5-fold cross-validation 앙상블로 학습된 모델을 동시에 실행해 결과를 투표한다.

```
CV1: 0.82 → Responder
CV2: 0.71 → Responder
CV3: 0.79 → Responder
CV4: 0.65 → Responder
CV5: 0.68 → Responder
────────────────────────
mean: 0.73 → Responder (5/5 투표)
```

고객에게 전달하는 메시지: **"단일 모델이 아니라 5개 모델이 동시에 검증하며, 투표 일치율이 높을수록 예측 신뢰도가 높다."**

### 입력 데이터 자동 검증

실행 전에 입력 GEX CSV의 컬럼 구성을 reference와 자동 비교한다.

```
match_ratio: 0.99  → PASS
missing_columns: []
extra_columns: [3개 추가 유전자 — 모델에서 무시됨]
```

고객에게 전달하는 메시지: **"데이터 품질 문제를 실행 전에 잡아준다. 잘못된 입력으로 결과를 믿는 상황을 방지한다."**

---

## 경쟁 포지션

| | DrugVLAB | 일반 response prediction tool |
|---|---|---|
| 입력 | 환자 GEX (bulk RNA-seq) | cell-line GEX |
| 출력 단위 | 환자 개인 | 세포주 평균 |
| 이질성 처리 | attention-weighted mixture | 없음 |
| 앙상블 신뢰도 | CV 투표 + 일치율 표시 | 단일 score |
| 데이터 보안 | 고객 환경 내 실행 | 외부 API 전송 |
| 근거 설명 | AI assistant + 검토 패키지 | score만 반환 |

---

## 대화 시나리오별 답변

### "정확도가 얼마나 되나요?"

> "모델은 GDSC-TCGA 간 translational alignment에서 검증됐습니다. 단, 저희는 정확도 숫자보다 **앙상블 투표 일치율**을 신뢰 지표로 제시합니다. 5개 모델이 모두 동의하는 예측과 3:2로 갈리는 예측을 동일하게 0.6으로 표시하는 대신, 두 경우를 구분해서 보여줍니다. 경계 구간 샘플은 추가 검토가 필요하다는 신호로 활용하는 것이 맞습니다."

### "우리 데이터를 어떻게 처리하나요?"

> "환자 데이터는 고객의 AWS VPC 또는 온프레미스 환경 안에서만 처리됩니다. DrugVLAB 서버로 전송되는 것은 없습니다. 모델 파일만 배포되고, 실행과 결과 저장 모두 고객 인프라 안에서 이루어집니다."

### "bulk RNA-seq 데이터가 없으면 안 되나요?"

> "현재 모델은 bulk RNA-seq 기반 ~1,000개 유전자 프로파일이 입력입니다. 실행 전 데이터 검증 단계에서 어떤 유전자가 있고 없는지를 확인해드리므로, 실제 데이터로 매칭 가능 여부를 먼저 테스트해볼 수 있습니다."

### "cell-line 수준 예측이랑 뭐가 다른가요?"

> "cell-line 예측은 특정 세포주에서 이 약이 효과적인가를 보는 것입니다. THERAPI는 **환자 샘플이 어떤 cell-line들과 유사한지**를 학습한 공통 좌표계 위에서 예측합니다. 같은 약물이라도 tissue type과 종양 이질성에 따라 다른 반응 패턴이 나오는 것을 반영합니다."

---

## 제품 흐름 (고객 화면 기준)

```
1. 데이터 업로드
   - input.csv: [index, smiles, gex_file_path]
   - gex.csv: 환자별 유전자 발현 matrix

2. 자동 검증
   - 유전자 컬럼 match 비율 확인
   - PASS/FAIL 즉시 표시

3. 실행
   - AWS Batch GPU 인스턴스에서 THERAPI 모델 실행
   - 환자 수에 따라 수 분 ~ 수십 분

4. 결과 확인
   - Decision Board: Responder/Non-Responder 분류 + 카운트
   - 샘플 목록: binaryMean 기준 정렬, 경계 구간 하이라이트
   - 개별 샘플: CV별 raw score + binary vote 상세

5. AI Assistant
   - "왜 이 샘플이 Responder인가" 질문 가능
   - 코호트 요약, 경계 구간 해석 가이드 제공

6. Review & Export (추가 예정)
   - reviewer의 go/hold/no-go 판정
   - Decision Card (JSON/PDF) 생성
```

---

## 초기 타겟 고객

| 세그먼트 | 구체적 사용 시나리오 |
|---|---|
| 종양학 임상시험 설계 팀 | 환자 코호트에서 responder 예상 비율 산출, enrichment 전략 수립 |
| 바이오마커 팀 | 반응군/비반응군 분리 후 차별 유전자 패턴 탐색 |
| 전임상-임상 translational 팀 | 동물/오가노이드 데이터와 환자 데이터 간 alignment 검증 |
| 병원 정밀의료 팀 | 기존 환자 데이터로 약물 후보 우선순위 내부 평가 |

---

## THERAPI vs PertDA — 두 모델의 정확한 차이

PertDA는 THERAPI의 대안이 아니라, THERAPI 위에 CSG2A와 Domain Adaptation을 결합한 **통합 고도화 모델**이다.

### 아키텍처 비교

| | THERAPI | PertDA (PANCDR-THERAPI-CSG2A-DA) |
|---|---|---|
| 환자 GEX 인코딩 | raw GEX encoder (VAE) | raw GEX encoder (동일) |
| 약물 표현 | GCN (SMILES graph) | GCN + **CSG2A compound embedding** |
| 세포 상태 표현 | raw GEX latent | raw GEX latent + **CSG2A perturbed GEX latent** |
| Domain shift 처리 | 없음 | **raw GEX DA + CSG2A-state DA** (적대적 학습) |
| 앙상블 | 5-fold | **10-fold** |
| 검증 AUROC (TCGA) | — | **0.757** (std: 0.032) |

### PertDA가 추가로 해결하는 문제

**1. 전임상→임상 도메인 갭 (Domain Adaptation)**

THERAPI를 포함한 대부분의 모델은 GDSC(cell-line)에서 학습한 패턴을 TCGA(환자)에 그냥 적용한다.
PertDA는 GDSC와 TCGA의 분포 차이를 적대적 Domain Adaptation으로 명시적으로 좁힌다.

```
학습 데이터: GDSC (cell-line, 전임상)
┌─────────────────────────────────────────┐
│ raw GEX DA: GDSC GEX 분포 ↔ TCGA GEX   │
│ CSG2A-state DA: perturbation 상태 정렬  │
└─────────────────────────────────────────┘
테스트: TCGA (환자, 임상) → AUROC 0.757
```

세일즈 언어: **"cell-line에서 잘 되던 약이 환자에게 안 된다는 문제를, 우리 모델은 도메인 정렬 학습으로 직접 다룹니다."**

**2. 약물 perturbation 효과 통합 (CSG2A 결합)**

THERAPI는 환자 GEX와 약물 SMILES를 독립적으로 인코딩한다.
PertDA는 CSG2A를 통해 "이 약이 이 환자의 유전자를 어떻게 변화시키는가"를 먼저 계산하고, 그 perturbation 패턴을 예측에 반영한다.

```
환자 GEX + SMILES
       ↓
CSG2A: perturbed GEX + compound embedding 생성
       ↓
"약 처리 후 세포 상태 변화" 반영 → response probability
```

세일즈 언어: **"약물의 화학 구조만 보는 게 아니라, 그 약이 환자 유전자에 실제로 미치는 변화까지 반영해서 예측합니다."**

### 출력 구조 (THERAPI와 동일 포맷, 추가 필드 있음)

```json
{
  "response_probability": 0.73,
  "response_probability_std_across_checkpoints": 0.041,
  "n_checkpoints": 10,
  "results": { "pred_fold_0_model": 0.71, "...", "pred_fold_9_model": 0.76 },
  "results_binary": { "pred_fold_0_model": 1, "..." },
  "results_binary_mean": 0.80,
  "csg2a_mode": "exact_csg2a_asg"
}
```

`csg2a_mode: exact_csg2a_asg` — CSG2A가 실제로 perturbed GEX와 compound embedding을 생성했음을 의미.

### 언제 THERAPI를, 언제 PertDA를 쓰나

| 상황 | 권장 모델 |
|---|---|
| 빠른 스크리닝, 대규모 코호트 초기 탐색 | THERAPI |
| 전임상→임상 translational 신뢰도가 중요한 후보 | PertDA |
| 약물 MoA까지 반영한 고신뢰 예측 필요 | PertDA |
| 두 모델 앙상블로 결과 교차 검증 | THERAPI + PertDA 동시 실행 |

두 모델을 동시에 실행하면 **"THERAPI 동의 + PertDA 동의 → 최고신뢰"** 로 계층화된 신뢰도 구조를 만들 수 있다.

```
THERAPI: Responder (0.78)
PertDA:  Responder (0.73)
→ Consensus Responder ← 회의에 올릴 수 있는 최강 근거

THERAPI: Responder (0.65)
PertDA:  Non-Responder (0.42)
→ Conflicted ← 추가 검토 필요 신호
```
