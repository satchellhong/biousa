# DrugVLAB × AWS 파트너십 전략 로드맵

> 회사: AIGENDRUG Co., Ltd.
> 플랫폼: DrugVLAB (AI 기반 신약개발 SaaS)
> 작성일: 2026-04-29
> 목표: AWS FTR 인증 → ISV Accelerate → AWS 공동 홍보 → 글로벌 진출

---

## 핵심 목표 요약

```
FTR 인증 취득
    ↓
AWS Partner Badge + Partner Solution Finder 등재
    ↓
ISV Accelerate 가입 → AWS 영업팀과 공동 딜 추진
    ↓
AI/ML 또는 Life Sciences Competency 취득
    ↓
AWS와 공동 마케팅 → 글로벌 고객 획득
```

**DrugVLAB이 AWS 파트너가 되어야 하는 이유**:
- AWS는 단순 인프라 공급자가 아닌 **세일즈 파트너** — ISV Accelerate 가입 시 AWS 영업팀이 글로벌 고객에게 DrugVLAB을 직접 추천
- AI/ML Competency 배지 = 기술 신뢰도 증명 → 해외 제약사/바이오 기업 영업 시 핵심 레퍼런스
- AWS Marketplace 등록 = 미국·유럽 고객이 자국 클라우드 예산으로 직접 구독 가능

---

## 현재 상황 분석

### AIGENDRUG 현재 위치

| 항목 | 상태 |
|---|---|
| AWS Software Path | ✅ Enrolled (등록됨) |
| APN 연회비 $2,500 납부 | ❓ 확인 필요 (미납 시 Confirmed 미달) |
| FTR 신청 | ⏸ FTR 현재 일시 중단(Paused) — 재개 대기 중 |
| 체크리스트 46개 항목 이행 | ⬜ 아직 시작 전 |
| CIS Benchmark 리포트 | ⬜ AWS Security Hub 미활성화 |
| Architecture Diagram | ⬜ 미작성 |
| AWS Marketplace 등록 | ⬜ 미등록 |
| ISV Accelerate | ⬜ FTR 이후 신청 가능 |

### DrugVLAB 기술 스택 — FTR 관점 평가

DrugVLAB은 이미 AWS 네이티브 아키텍처를 사용 중이라 FTR 기술 요건 다수를 빠르게 충족할 수 있다.

| AWS 서비스 | FTR 관련 항목 | 현황 예상 |
|---|---|---|
| Cognito | IAM-001, IAM-004, IAM-011 (MFA, 개인 신원) | 🟡 설정 확인 필요 |
| Secrets Manager | IAM-009, IAM-010 (시크릿 하드코딩 금지) | 🟢 활용 중일 가능성 높음 |
| VPC + ALB + WAF | NETSEC-001, NETSEC-002 (네트워크 보안) | 🟡 보안그룹 규칙 검토 필요 |
| S3 | S3-001 (버킷 접근 수준) | 🟡 퍼블릭 버킷 여부 확인 필요 |
| EFS + S3 (데이터 레이어) | SDAT-002, SDAT-003 (암호화) | 🟡 암호화 설정 확인 필요 |
| Batch + Lambda + ECS | HOST-001 (AWS 위에서 실행) | 🟢 충족 |
| 미설정 | Security Hub + CIS Benchmark | ⬜ 활성화 필요 |

---

## Phase 1 — FTR 준비 (지금 ~ FTR 재개 시)

> 목표: FTR 재개 즉시 신청 가능한 상태 만들기
> 예상 소요: 4~8주

### 1-1. 즉시 처리 가능한 항목 (각 30분 이내)

| 우선순위 | 항목 | 방법 |
|---|---|---|
| 1 | AWS 계정 연락처 설정 (CIS Account.1) | AWS Console → Account → Alternate Contacts |
| 2 | root 계정 액세스 키 제거 (CIS IAM.4) | IAM Console → Security credentials → Access keys |
| 3 | root 계정 MFA 활성화 | IAM Console → Security credentials → MFA |
| 4 | IAM 비밀번호 정책 설정 (14자 이상, 재사용 방지) | IAM → Account settings → Password policy |
| 5 | 기본 VPC 보안그룹 인바운드 규칙 제거 (CIS EC2.2) | EC2 → Security Groups → default |

### 1-2. AWS Security Hub 활성화 (1~2일)

```
AWS Console → Security Hub → Enable
→ CIS AWS Foundations Benchmark v3.0 표준 활성화
→ 24~48시간 후 CIS 리포트 자동 생성
```

**목적**: FTR 제출 시 CIS 리포트를 함께 내면 **30분 내 자동 승인** 가능.
미제출 시 AWS PSA 수동 검토로 수 주 지연될 수 있다.

**필수 통과 항목 8개**:
- IAM.4 (root 액세스 키 없음)
- IAM.5 (IAM 유저 전원 MFA)
- IAM.3 (정적 자격증명 모니터링)
- IAM.15 / IAM.16 (비밀번호 정책 14자, 재사용 방지)
- EC2.54 / EC2.53 (보안그룹 최소 권한)
- EC2.2 (기본 VPC 보안그룹 트래픽 차단)
- Account.1 (계정 연락처 설정)

### 1-3. 아키텍처 문서화 (1~2주)

**Architecture Diagram** (필수 제출):
- 도구: draw.io / Lucidchart / AWS Architecture Icons
- 포함 내용: VPC 구성, Batch/ECS/Lambda 흐름, ALB/WAF, S3/EFS, Cognito, Secrets Manager
- 형식: PNG/JPEG

**체크리스트 46개 항목 이행**:
- `docs/FTR_상세_절차.md` 참고
- DrugVLAB이 고객 AWS 계정에 접근하지 않는다면 CAA-001~007 (Cross-Account 7개) → ➖ 해당없음 처리 가능
- 실질 이행 대상: ~39개 항목

### 1-4. APN 연회비 확인

- Partner Central → Home → 연회비 납부 여부 확인
- 미납 시 $2,500 납부 → Confirmed 단계 진입 → Promotional Credits 등 혜택 활성화

---

## Phase 2 — FTR 신청 및 Validated 달성

> 목표: AWS Validated 파트너 인증 취득
> 예상 소요: FTR 재개 후 1~4주

### 2-1. FTR 신청 절차

```
Partner Central
→ Build → Solutions → DrugVLAB 솔루션 선택
→ Request Validation 클릭
→ 업로드:
   □ FTR Self-Assessment 엑셀 (docs/FTR_Self_Assessment.xlsx)
   □ CIS Benchmark 리포트 (Security Hub에서 CSV 다운로드)
   □ Architecture Diagram (PNG)
→ 자동 심사 (30분) 또는 AWS PSA 수동 검토
```

### 2-2. FTR 단축 경로 (해당 시 활용)

| 방법 | 조건 | 효과 |
|---|---|---|
| WAFR 면제 | 12개월 내 AWS 직원/WAPP 파트너 수행 WAFR + HRI 0건 | 46개 → 5개 항목만 확인 |
| SOC 2 Type II | 현재 유효, AWS in scope, unqualified opinion | 45개 → 11개 항목 |

### 2-3. Validated 달성 시 즉시 활성화할 것들

| 순서 | 행동 | 효과 |
|---|---|---|
| 1 | AWS Partner Badge 다운로드 → 웹사이트/자료에 부착 | 공식 인증 마크로 신뢰도 상승 |
| 2 | Partner Solution Finder 프로필 완성 | AWS.com에서 고객에게 노출 |
| 3 | **ISV Accelerate 신청** | AWS 영업팀 Co-sell 시작 (가장 중요) |
| 4 | AWS Marketplace 등록 진행 | 글로벌 구독 채널 개설 |
| 5 | ACE Pipeline Manager 활성화 | AWS로부터 Referral 수신 시작 |

---

## Phase 3 — ISV Accelerate & AWS Marketplace (FTR 후 1~3개월)

> 목표: AWS와 공동 글로벌 영업 체계 구축

### 3-1. ISV Accelerate

**이것이 AWS 파트너십에서 가장 중요한 혜택이다.**

- AWS Account Manager들이 DrugVLAB을 고객에게 직접 추천
- Marketplace Private Offer로 딜 성사 시 AWS AM에게 인센티브 → 적극 추천 동기 부여
- 파트너의 51%가 AWS Co-sell 결과로 더 높은 매출 성장 경험
- 신청: Partner Central → Programs → ISV Accelerate

**DrugVLAB에게 특히 유리한 이유**:
- AWS는 Life Sciences / Biotech 분야 대형 고객(제약사, CRO, 연구소)과 이미 계약 관계
- DrugVLAB을 AWS AM이 기존 계약 고객에게 추천 → 신규 영업 기회 창출
- AI/ML on AWS 스토리로 AWS 홍보 자료에 포함될 가능성

### 3-2. AWS Marketplace 등록

- 미국·유럽 고객이 자국 AWS 계정 크레딧/예산으로 DrugVLAB 직접 구독 가능
- Enterprise 고객은 Marketplace를 통한 구매를 강하게 선호 (조달 프로세스 단축)
- Private Offer: 개별 고객사와 가격 협상 후 Marketplace를 통해 계약 처리

**등록 준비물**:
- 솔루션 소개 자료 (영문)
- 가격 모델 정의 (per user / compute / custom)
- 기술 통합 문서

### 3-3. ACE & POA 펀딩

- ACE Pipeline Manager: AWS와 영업 기회 공동 관리 → Referral 수신
- POA Funding: 딜 클로저 가속을 위한 마케팅/PoC 비용 AWS 지원
- 신규 기회 창출 시 금전적 인센티브

---

## Phase 4 — AWS Competency 취득 (12개월+)

> 목표: Life Sciences 또는 AI/ML Competency → 최고 수준의 차별화

### 4-1. DrugVLAB에 적합한 Competency

| Competency | 적합성 | 이유 |
|---|---|---|
| **Life Sciences** | ⭐⭐⭐ 최우선 | 신약개발 SaaS, 생명과학 분야 직접 해당 |
| **AI/ML Software** | ⭐⭐⭐ 최우선 | Hot2Mol, MixingDTA, AutoGluon 등 AI 모델 핵심 |
| **Genomics** | ⭐⭐ 검토 필요 | 파이프라인 특성에 따라 해당될 수 있음 |
| Healthcare | ⭐ 보류 | 직접 의료 서비스 아닌 연구 도구라 요건 미충족 가능성 |

**Life Sciences + AI/ML 동시 취득 전략**:
두 Competency는 상호 보완적. Life Sciences는 산업 신뢰도, AI/ML은 기술 신뢰도를 각각 증명.
AWS re:Invent 및 AWS Life Sciences Summit에서 함께 홍보 가능.

### 4-2. Competency 취득 요건

- FTR(Validated) 완료
- 고객 레퍼런스 케이스 (검증된 고객 성공 사례)
- 기술 검증 (AWS 전문가 심사)
- 소요 기간: 수개월

### 4-3. Competency 달성 후 혜택

- AWS 공식 홍보 자료에 AIGENDRUG 로고 및 솔루션 노출
- Partner Solution Finder 상위 랭킹
- AWS 전문가와의 기술 협업 세션
- APN 블로그 성공 사례 게재 가능
- re:Invent 등 AWS 이벤트 스폰서십 기회

---

## 글로벌 진출 전략

### AWS를 통한 해외 진출 경로

```
국내 안정화 → FTR 인증 → AWS와 Co-sell → 미국/유럽 제약사 접근
                              ↓
                     AWS Life Sciences 고객 추천
                     (Pfizer, Novartis, Roche 등
                      AWS 계약 대형 제약사)
```

### 거점 시장 우선순위

| 시장 | 이유 | AWS 활용 포인트 |
|---|---|---|
| 미국 | 세계 최대 바이오/제약 시장, AWS 본사 | ISV Accelerate, Marketplace |
| 유럽 (영국/독일) | 신약개발 강국, EU AI법 대응 니즈 | GDPR 대응 아키텍처가 강점 |
| 일본 | 아시아 최대 제약 시장, AWS Japan 적극적 | AWS Japan과 공동 마케팅 |
| 중동 (UAE/사우디) | AWS Summit Middle East, 대규모 헬스케어 투자 | AWS Healthcare 프로그램 연계 |

### AWS를 통한 공동 홍보 활용

| 채널 | 방법 |
|---|---|
| AWS Partner Blog | Validated 이후 신청 가능, DrugVLAB 성공 사례 영문 기고 |
| AWS re:Invent | Competency 취득 후 스폰서십 또는 Startup Showcase 참여 |
| AWS Summit Seoul | 국내 홍보 + 글로벌 네트워킹 기회 |
| AWS Solution Library | 솔루션 등재 → AWS 고객이 직접 탐색 |
| APN TV | 파트너 소개 영상 제작 및 배포 |
| AWS Press Release | AWS와 공동 보도자료 발행 (주요 딜 성사 시) |

---

## 전체 타임라인

```
2026년 4~6월 (지금)
├── APN 연회비 납부 확인 (Confirmed 단계 진입)
├── Security Hub + CIS Benchmark 활성화
├── 즉시 처리 가능 항목 완료 (1~2일)
├── FTR 체크리스트 46개 이행 시작
└── Architecture Diagram 작성 시작

2026년 6~8월
├── 체크리스트 46개 이행 완료
├── CIS 리포트 8개 항목 모두 PASSED 확인
├── FTR 재개 시 즉시 신청
└── AWS Marketplace 등록 준비

2026년 8~12월 (FTR 승인 후)
├── ✅ Validated 단계 달성
├── AWS Partner Badge 부착
├── Partner Solution Finder 등재
├── ISV Accelerate 신청 즉시
├── ACE 파이프라인 활성화
└── AWS Marketplace 정식 등록

2027년 (Competency 추진)
├── 고객 레퍼런스 확보 (국내/해외 1~2건)
├── Life Sciences Competency 신청
├── AI/ML Competency 신청
└── AWS와 공동 마케팅 캠페인 개시
```

---

## 지금 당장 해야 할 일 (우선순위 순)

| # | 할 일 | 소요 시간 | 담당 |
|---|---|---|---|
| 1 | APN 연회비 납부 여부 확인 (Partner Central) | 10분 | - |
| 2 | AWS 계정 연락처 설정 (CIS Account.1) | 5분 | - |
| 3 | root 계정 액세스 키 제거 (CIS IAM.4) | 5분 | - |
| 4 | IAM 비밀번호 정책 설정 (14자, 재사용 방지) | 10분 | - |
| 5 | AWS Security Hub 활성화 + CIS 표준 활성화 | 1시간 | - |
| 6 | 기본 VPC 보안그룹 인바운드 규칙 제거 | 30분 | - |
| 7 | IAM 유저 전원 MFA 활성화 | 30분/인 | - |
| 8 | Architecture Diagram 작성 시작 | 1~2주 | - |
| 9 | FTR_상세_절차.md 보며 체크리스트 항목별 이행 | 4~6주 | - |

> 1~7번은 모두 합쳐 반나절이면 완료 가능. 지금 바로 시작하는 것이 최우선.

---

## 참고 문서

| 문서 | 경로 |
|---|---|
| DrugVLAB 플랫폼 소개 | `docs/DrugVLAB_소개.md` |
| AWS Software Path 전체 혜택 | `docs/AWS_파트너_전체_로드맵.md` |
| FTR 전체 절차 + 항목별 이행 방법 | `docs/FTR_상세_절차.md` |
| FTR 체크리스트 항목별 상세 이행 방법 | `docs/FTR_상세_절차.md` |
| FTR 가이드 PDF (Jan 2026) | `docs/AWS_FTR_Guide_latest.pdf` |
| Self-Assessment 엑셀 | `docs/FTR_Self_Assessment.xlsx` |
| 한국어 체크리스트 | `docs/FTR_Checklist_KO.html` |
