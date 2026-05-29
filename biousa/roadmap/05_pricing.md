# DrugVLAB — 가격 패키지

## 설계 원칙

좌석 기반 단독 과금은 약하다. DrugVLAB의 가치는 "UI 접속권"이 아니라 "운영되는 분석 환경"에서 나오므로, 아래 4개 축을 조합한다.

1. **기본 플랫폼 사용료** — 환경 운영 고정비
2. **분석 실행량** — 크레딧 소진 기반 (기존 크레딧 시스템 활용)
3. **프라이빗 배포비** — 고객 VPC/온프레미스 배포 시 추가
4. **온보딩 fee** — 초기 데이터 연결 + 커스터마이징

---

## 패키지

### Explorer
**대상**: Discovery 팀 / 소규모 바이오텍

| 항목 | 내용 |
|---|---|
| 포함 모듈 | Cohort Twin + Response Explorer |
| 사용자 | 최대 5명 |
| 실행 환경 | DrugVLAB 공용 클라우드 (SaaS) |
| Review workflow | 포함 (go/hold/no-go + memo) |
| Export | JSON report |
| 기본료 | 월 정액 (플랫폼 운영) |
| 실행 과금 | 크레딧 소진 방식 |
| 지원 | 이메일 |

---

### Translator
**대상**: Translational science 팀 / 중형 제약사

| 항목 | 내용 |
|---|---|
| 포함 모듈 | Cohort Twin + Response Explorer + Mechanism Lens |
| 사용자 | 최대 20명 |
| 실행 환경 | DrugVLAB 공용 클라우드 (SaaS) |
| Review workflow | 포함 + Decision History 전체 |
| Export | JSON + PDF report |
| 기본료 | 월 정액 (Explorer × 2.5) |
| 실행 과금 | 크레딧 소진 방식 (Explorer보다 높은 단가 cap 가능) |
| 지원 | 이메일 + 전화 |

---

### Private Runtime
**대상**: 데이터 보안 요건이 있는 대형 제약사 / 병원

| 항목 | 내용 |
|---|---|
| 포함 모듈 | 전체 (Cohort Twin + Response Explorer + Mechanism Lens) |
| 사용자 | 무제한 (내부 Cognito 연동 또는 SSO) |
| 실행 환경 | 고객 AWS VPC 또는 온프레미스 |
| 데이터 정책 | No-data-egress (데이터 반출 없음) |
| Review workflow | 포함 + RBAC + audit log |
| Export | JSON + PDF + 커스텀 포맷 |
| 기본료 | 연간 계약 (라이선스 + 유지보수) |
| 배포비 | 초기 1회성 setup fee |
| 실행 과금 | 고객 자체 AWS 비용 부담 (DrugVLAB 과금 없음) |
| 지원 | 전담 CSM + SLA |

---

### Report Generator (Add-on)
**대상**: Explorer 또는 Translator 위에 얹는 애드온

| 항목 | 내용 |
|---|---|
| 기능 | Review packet 생성, PDF export, 회의용 markdown summary |
| 추가 요금 | 월 정액 소량 추가 |

---

## 과금 흐름 (기존 크레딧 시스템 활용)

기존에 구축된 크레딧 시스템(`billing-engine`, DynamoDB ledger, Athena 집계)을 그대로 활용한다.

```
[실행 요청]
    → credit 잔액 확인 (기존 MyBalanceView)
    → 실행 시작 시 credit hold (기존 reservation-hold-ddb)
    → 완료 시 credit 차감 (기존 settlement-worker-lambda)

[Review / Export]
    → 별도 크레딧 차감 없음 (기본 플랫폼 사용료에 포함)
    → PDF export는 생성 1건당 소량 크레딧 차감 (선택)
```

---

## AWS FTR 관점 추가 가치

Private Runtime 패키지는 AWS FTR(Foundational Technical Review) 통과 이후 AWS Marketplace 등록을 통해 채널 확장이 가능하다.

- AWS Marketplace: 고객 AWS 계정에서 직접 구독 → 도입 마찰 최소화
- ISV Accelerate 프로그램 연계: AWS 영업 채널을 통한 enterprise 고객 접근
- Well-Architected 기준 충족을 판매 근거로 활용 (security, reliability, operational excellence)
