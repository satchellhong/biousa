# DrugVLAB — 제품 정의

## 한 줄 정의

DrugVLAB은 제약사·병원·바이오텍의 내부 데이터 환경에서 실행되며, 후보 생성·반응 예측·메커니즘 해석·환자 정렬 결과를 검토 가능한 evidence package로 묶어 의사결정을 표준화하는 **translational decision-support SaaS**다.

---

## 포지셔닝

| 경쟁 포지션 | DrugVLAB 포지션 |
|---|---|
| "더 잘 맞히는 AI 모델" | "검토 가능한 evidence package" |
| "범용 drug discovery platform" | "oncology 중심 translational decision cockpit" |
| "예측 결과를 제공하는 분석 서비스" | "승인·반려·기록이 연결된 의사결정 운영체계" |

고객이 사는 것은 모델이 아니라, **보안 제약이 큰 조직에서도 도입 가능한 의사결정 운영체계**다.

---

## 핵심 가치 4축

| 가치 축 | 고객이 얻는 것 |
|---|---|
| **Data stays inside** | 고객 VPC 또는 온프레미스에서 실행. 데이터 반출 없음 |
| **Translational alignment** | 내부 샘플을 preclinical reference 위에서 해석 가능한 공통 좌표계로 정렬 (THERAPI) |
| **Mechanism-aware evidence** | perturbation, pathway, MoA 유사성까지 연결된 설명 (CSG2A) |
| **Review workflow** | 결과 확인 → 승인/반려/코멘트 → 보고서 생성까지 연결된 운영 흐름 |

---

## 기존 기능의 재배치

현재 DrugVLAB의 분석 엔진들은 버릴 것이 없다. 제품 레이어만 재정의한다.

| 현재 기능 | 새 제품 안에서의 역할 |
|---|---|
| Kinase / PPI molecule generation | "추천 가능한 후보군 생성" 레이어 |
| Docking / PLIP / affinity / ranking | "근거 수집 및 후보 검증" 레이어 |
| CSG2A (preclinical drug response) | "메커니즘 근거와 MoA evidence" 레이어 |
| THERAPI (clinical drug response) | "환자/코호트 맥락 정렬과 translation evidence" 레이어 |

---

## 피해야 할 메시지

- "최고 성능 AI 모델"
- "모든 오믹스와 모든 질환을 커버하는 통합 AI"
- "범용 drug discovery platform"

이런 표현은 검증 부담만 키우고 지금 가진 자산의 강점을 희석시킨다.

---

## 강조해야 할 메시지

- 내부 데이터를 밖으로 내보내지 않고 후보 판단을 지원하는 **private decision-support SaaS**
- 환자/샘플과 전임상 모델 간의 gap을 줄여주는 **translational alignment layer**
- 유사 약물과 MoA 근거까지 제시하는 **explanation-native review system**
