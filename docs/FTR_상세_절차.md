# AWS FTR 상세 절차 가이드

> 대상: AIGENDRUG Co., Ltd. — Partner Hosted on AWS (SaaS)
> 체크리스트 버전: Feb 2026 – Aug 2026
> 현재 FTR 상태: **일시 중단(Paused)** — 재개 시 Partner Central에서 신청 가능

---

## 진행 현황 한눈에 보기

> 상태: ⬜ 미착수 / 🔄 진행중 / ✅ 완료 / ❌ FAIL(조치필요) / ➖ 해당없음
>
> 검증 방식: 🤖 IaC 자동검증 (`ftr_validate_iac`) / 🔍 boto3 자동점검 (`ftr_check_console`) / 🖥️ 콘솔 직접 확인 / 📄 문서 작성
>
> **최종 업데이트**: 2026-04-29 — `ftr_full_report()` 통합 점검 결과 반영

### 사전 요구사항

| ID | 항목 | 검증 방식 | 상태 |
|---|---|---|---|
| CIS | CIS Benchmark 리포트 생성 (Security Hub) | 🔍 boto3: Security Hub 활성화 여부 자동 확인 | ❌ Security Hub 비활성화 |
| GA | 솔루션 GA 상태 확인 | 📄 내부 확인 | ⬜ |
| HOST-001 | 핵심 컴포넌트 AWS 실행 확인 + Architecture Diagram | 📄 다이어그램 작성 | ⬜ |
| SUP-001 | Business Support 구독 또는 대응 계획 수립 | 🔍 boto3: Support API로 티어 자동 확인 | ❌ Basic Support (Business 이상 필요) |
| WAFR-001 | 연 1회 아키텍처 검토 수행 | 📄 Well-Architected Tool 또는 내부 문서 | ⬜ |
| WAFR-002 | AWS 공동 책임 모델 검토 완료 | 📄 내부 문서 | ⬜ |

### 루트 계정

| ID | 항목 | 검증 방식 | 상태 |
|---|---|---|---|
| ARC-001 | 루트 계정 MFA 활성화 | 🔍 boto3: AccountMFAEnabled 자동 확인 | ✅ MFA 활성화 확인 |
| ARC-004 | 루트 액세스 키 제거 (CIS IAM.4) | 🔍 boto3: AccountAccessKeysPresent 자동 확인 | ❌ 루트 액세스 키 1개 존재 — 즉시 삭제 필요 |
| ARC-005 | 루트 침해 IR 런북 작성 | 📄 런북 문서 작성 | ⬜ |

### AWS 커뮤니케이션

| ID | 항목 | 검증 방식 | 상태 |
|---|---|---|---|
| ACOM-001 | 계정 연락처 3개 설정 (CIS Account.1) | 🔍 boto3: Account API Alternate Contacts 자동 확인 | ❌ BILLING / OPERATIONS / SECURITY 모두 미설정 |
| ACOM-002 | 회사 소유 이메일/전화번호 사용 | 🖥️ ACOM-001 설정 시 함께 처리 | ⬜ |

### IAM

| ID | 항목 | 검증 방식 | 상태 |
|---|---|---|---|
| IAM-001 | 모든 IAM 사용자 MFA (CIS IAM.5) | 🔍 boto3: list_users + list_mfa_devices 자동 확인 | ❌ MFA 미설정 5명: hyerinkim, seokcholhong, sugyunan, tester, youngkukkim |
| IAM-002 | 자격증명 90일 교체 (CIS IAM.3) | 🔍 boto3: Credential Report 파싱 자동 확인 | ❌ 90일 초과 키 8개 (최대 1167일 미교체) |
| IAM-003 | 비밀번호 정책 14자+재사용방지 (CIS IAM.15+16) | 🔍 boto3: get_account_password_policy 자동 확인 | ❌ 비밀번호 정책 미설정 |
| IAM-004 | 개인별 신원, 공유 계정 금지 | 🖥️ IAM → Users 목록 검토 | ⬜ |
| IAM-005 | 제3자 접근에 IAM 역할 사용 | 🤖 IaC: identity_access_iam 모듈 확인 | ✅ |
| IAM-006 | 최소 권한 원칙 | 🤖 IaC: AdministratorAccess/PowerUserAccess 정책 없음 확인 + 🖥️ Access Analyzer | ✅ |
| IAM-007 | 생명주기 기반 접근 관리 | 📄 온보딩/오프보딩 체크리스트 | ⬜ |
| IAM-008 | 분기별 신원 감사 | 📄 감사 일정/기록 | ⬜ |
| IAM-009 | 코드에 자격증명 하드코딩 금지 | 🤖 IaC: AKIA 키 패턴 및 secret_access_key 직접 할당 없음 확인 | ✅ |
| IAM-010 | 시크릿 Secrets Manager 저장 | 🤖 IaC: secrets_manager + discovery_ssm 모듈 확인 | ✅ |
| IAM-011 | 고객 자격증명 암호화/해싱 | 📄 코드 리뷰 (앱 코드에서 bcrypt/Argon2 사용 여부) + 🤖 auth_cognito 모듈 부분 확인 | ⬜ |
| IAM-012 | 앱에서 임시 자격증명 사용 | 🤖 IaC: identity_access_iam 모듈(EC2/ECS/Lambda IAM Role) 확인 | ✅ |

### 운영 보안 / 네트워크 / 백업 / 탄력성

| ID | 항목 | 검증 방식 | 상태 |
|---|---|---|---|
| SECOPS-001 | 취약점 관리 프로세스 | 📄 취약점 관리 정책 문서 | ⬜ |
| OPS | CloudTrail 감사 로그 활성화 | 🔍 boto3: describe_trails 자동 확인 | ❌ CloudTrail trail 없음 |
| NETSEC-001 | 보안그룹 최소 권한 (CIS EC2.53+54) | 🤖 IaC: 0.0.0.0/0+프로토콜-1 ingress 없음 + prod SSH allow_ssh=false 조건 확인 | ✅ |
| NETSEC-002 | 기본 VPC SG 트래픽 차단 (CIS EC2.2) | 🔍 boto3: describe_security_groups(default) 자동 확인 | ❌ 3개 VPC 기본 SG 모두 규칙 존재 (inbound 1 + outbound 1) |
| BAR-001 | 자동 백업 구성 | 🤖 IaC: DynamoDB PITR(7개 테이블) + S3 versioning status=Enabled(10개) 확인 | ✅ |
| BAR-002 | 백업 복구 테스트 | 📄 복구 테스트 기록 | ⬜ |
| RES-001 | RPO 정의 | 📄 DR/런북 문서 | ⬜ |
| RES-002 | RTO 정의 | 📄 DR/런북 문서 | ⬜ |
| RES-004 | 탄력성 테스팅 | 📄 장애 주입 테스트 기록 | ⬜ |
| RES-005 | 고객에게 탄력성 책임 고지 | 📄 서비스 약관/SLA 문서 | ⬜ |
| RES-006 | 업타임 SLA 달성 아키텍처 | 🤖 IaC: 4개 AZ 서브넷 정의 + load_balancer_alb 모듈 확인 | ✅ |
| RES-007 | 장애 시 고객 커뮤니케이션 계획 | 📄 장애 대응 커뮤니케이션 절차 | ⬜ |

### S3 / Cross-Account / 민감 데이터 / 규제

| ID | 항목 | 검증 방식 | 상태 |
|---|---|---|---|
| S3-001 | S3 버킷 접근 권한 검토 | 🤖 IaC: public_access_block 4개 파라미터 전부 true(10개 버킷) + DenyInsecureTransport(8개) + SSE-KMS(9개) 확인 | ✅ |
| CAA-001~007 | Cross-Account 접근 (고객 계정 접근 없으면 ➖) | ➖ | ➖ |
| SDAT-001 | 민감 데이터 식별 | 📄 데이터 분류 문서 | ⬜ |
| SDAT-002 | 저장 데이터 암호화 | 🤖 IaC: DynamoDB SSE(8개 테이블) + S3 SSE-KMS(9개) + aws_kms_key 3개 모두 key rotation=true 확인 | ✅ |
| SDAT-003 | 전송 중 암호화 (TLS) | 🤖 IaC: generic_acm + load_balancer_alb 모듈 + S3 DenyInsecureTransport(8개) 확인 | ✅ |
| RCVP-001 | 컴플라이언스 준수 프로세스 | 📄 컴플라이언스 정책 문서 | ⬜ |

---

## 목차

1. [전체 흐름 요약](#1-전체-흐름-요약)
2. [FTR 신청 전 사전 확인](#2-ftr-신청-전-사전-확인)
3. [제출 서류 준비](#3-제출-서류-준비)
4. [체크리스트 항목별 상세 및 이행 방법](#4-체크리스트-항목별-상세-및-이행-방법)
5. [CIS Benchmark 리포트 생성](#5-cis-benchmark-리포트-생성)
6. [FTR 신청 절차](#6-ftr-신청-절차)
7. [심사 이후 프로세스](#7-심사-이후-프로세스)
8. [단축 경로 (WAFR / SOC 2)](#8-단축-경로)
9. [FTR 이후 — Software Path Validated 혜택](#9-ftr-이후--software-path-validated-혜택)

---

## 1. 전체 흐름 요약

```
[ 준비 단계 ]
  1. Software Path 등록 + APN 연회비 $2,500 납부 (Confirmed 단계)
  2. 체크리스트 46개 항목 자가 진단 및 이행
  3. CIS Benchmark 리포트 생성 (AWS Security Hub)
  4. Architecture Diagram 작성

[ 신청 단계 ]  ← 현재 Paused
  5. Partner Central → Build → Solutions → Request Validation
  6. 서류 업로드 (엑셀 + CIS 리포트 + Architecture Diagram)
  7. 자동 심사 (30분) 또는 AWS PSA 수동 검토

[ 승인 이후 ]
  8. Validated 단계 진입 → AWS Partner Badge, ISV Accelerate 등 혜택 활성화
  9. 3년 후 갱신 필요
```

---

## 2. FTR 신청 전 사전 확인

### 2-1. Software Path 등록 여부
- Partner Central → Home → Overview에서 **Partner Path: Software Path** 확인
- AIGENDRUG는 현재 Software Path + Services Path 둘 다 등록됨 ✅

### 2-2. APN 연회비 납부 (Confirmed 단계)
- $2,500 USD/년, AWS 연동 계정으로 청구
- **주의**: 2025년 11월 19일부터 AWS 계정 미연동 시 APN 혜택 상실
- Partner Central → Home → "get started here" 링크로 AWS 계정 연동 확인

### 2-3. 솔루션 등록 확인
- Partner Central → Build → Solutions에 FTR 대상 솔루션이 등록되어 있어야 함
- 없으면 "Create solution" 버튼으로 신규 생성

---

## 3. 제출 서류 준비

| 서류 | 필수 | 형식 | 생성 방법 |
|---|---|---|---|
| Self-Assessment 체크리스트 | ✅ | .xlsx | `docs/FTR_Self_Assessment.xlsx` 작성 |
| CIS Benchmark 리포트 | 권장 (없으면 수동 검토) | .csv | AWS Security Hub |
| Architecture Diagram | ✅ | .png / .jpeg | draw.io, Lucidchart 등 |

> CIS 리포트 + Architecture Diagram 동시 제출 → **30분 내 자동 승인** 가능  
> CIS 리포트 없이 제출 → AWS PSA가 이메일로 연락 후 수동 진행

---

## 4. 체크리스트 항목별 상세 및 이행 방법

> 상태 표시: ⬜ 미착수 / 🔄 진행중 / ✅ 완료 / ➖ 해당없음

---

### 4-0. 전제 조건

#### ✅ 1.1 Software Path 멤버십
**요구사항**: AWS Software Path에 등록되어 있어야 함  
**확인 방법**: Partner Central → Home → Partner Path 확인  
**현재 상태**: ⬜ 확인 필요

---

### 4-1. 사전 요구사항 (Prerequisites)

#### ⬜ CIS — CIS Benchmark 리포트
**요구사항**: AWS Security Hub로 CIS AWS Foundations Benchmark 스캔 후 CSV 리포트 제출  
**필수 여부**: 선택이지만 제출 시 자동 승인 가능  
**이행 방법**:
```
1. AWS Console → Security Hub → 활성화
2. Standards → CIS AWS Foundations Benchmark 활성화
3. 스캔 완료(수 시간) 후 View Results → Download (CSV)
4. 모든 필수 8개 항목 PASSED 확인 후 제출
```
> 비용: Security Hub 30일 무료 후 유료. AWS Config 활성화 필요 (Config도 유료)

---

#### ⬜ GA — 솔루션 일반 구매 가능 여부
**요구사항**: 제출 솔루션이 GA 상태이거나 고객이 구매 가능한 상태여야 함  
**이행 방법**: 현재 솔루션이 실제 판매/제공 중인지 확인. 베타/내부 테스트 전용이면 안 됨

---

#### ⬜ HOST-001 — 호스팅 모델 확인
**요구사항**: 제품의 모든 핵심 컴포넌트가 AWS에서 실행됨을 확인. Architecture Diagram 필수 제출  
**허용 예외**: CDN, DNS, 기업 IdP는 AWS 외부 사용 허용  
**이행 방법**:
```
1. 아키텍처 구성 요소 목록 작성
2. 각 컴포넌트가 AWS 서비스인지 확인
3. 타사 서비스가 있다면 CDN/DNS/IdP 해당 여부 확인
4. Architecture Diagram 작성 (draw.io 권장)
   - 포함 내용: VPC, 서브넷, 서비스 구성, 데이터 흐름, 외부 연동
```

---

#### ⬜ SUP-001 — AWS 지원 플랜
**요구사항**: 모든 프로덕션 AWS 계정에 Business Support 이상 구독, 또는 AWS 지원 없이 이슈를 처리할 계획 수립  
**Business Support 비용**: 월 $100 또는 AWS 사용 요금의 10% 중 큰 금액  
**이행 방법 (A — Business Support 구독)**:
```
AWS Console → 우측 상단 계정 → Support → Support Plans → Business 선택
```
**이행 방법 (B — 행동 계획 수립)**:
```
문서 작성: "AWS 지원이 필요한 상황 발생 시 처리 방안"
예시: 심각도별 내부 에스컬레이션 경로, 임시 Developer Support 업그레이드 절차 등
```

---

#### ⬜ WAFR-001 — 연간 아키텍처 검토
**요구사항**: 연 1회 이상 AWS 모범 사례 기반 아키텍처 검토 수행 및 문서화  
**이행 방법**:
```
A) AWS Well-Architected Tool 사용 (무료)
   AWS Console → Well-Architected Tool → Workload 생성 → 검토 수행
   → 리포트 다운로드 (FTR 제출 시 활용 가능)

B) 내부 아키텍처 검토 문서 작성
   - 검토 날짜, 검토자, 주요 발견사항, 개선 계획 포함
```

---

#### ⬜ WAFR-002 — AWS 공동 책임 모델 검토
**요구사항**: AWS Shared Responsibility Model (보안 + 탄력성) 검토 완료  
**이행 방법**:
```
1. https://docs.aws.amazon.com/whitepapers/latest/aws-risk-and-compliance/shared-responsibility-model.html 검토
2. AIGENDRUG가 책임지는 영역 문서화:
   - 운영체제, 네트워크 설정, 방화벽, 암호화, 애플리케이션
3. AWS가 책임지는 영역 확인:
   - 물리 인프라, 하이퍼바이저, 관리형 서비스 내부
```

---

### 4-2. AWS 루트 계정

#### ⬜ ARC-001 — 루트 사용자 예외적 사용
**요구사항**: 루트 계정은 일상 업무에 사용 금지. 최초 IAM 사용자 생성 후 루트 잠금  
**이행 방법**:
```
1. AWS Console → IAM → 관리자 IAM 사용자 생성 (없는 경우)
2. 루트 계정 MFA 활성화
3. 루트 계정 비밀번호를 팀 비밀번호 관리자(1Password 등)에 보관
4. 일상 업무는 IAM 사용자 또는 SSO로만 접근
```

---

#### ⬜ ARC-004 — 루트 액세스 키 제거 (CIS IAM.4)
**요구사항**: 루트 계정의 API 액세스 키가 존재하면 즉시 삭제  
**이행 방법**:
```
AWS Console → 우측 상단 계정명 → Security Credentials
→ "Access keys" 섹션에 키가 있으면 Delete 클릭
```
> CIS Benchmark에서 자동 검사됨. PASSED가 되어야 FTR 통과

---

#### ⬜ ARC-005 — 루트 계정 침해 IR 런북
**요구사항**: 루트 계정이 무단 사용될 경우 대응 절차 문서화  
**이행 방법**: 다음 내용 포함한 런북 문서 작성
```
[루트 계정 침해 대응 런북]
1. 즉시 루트 비밀번호 변경
2. 루트 MFA 재설정
3. 기존 루트 액세스 키 삭제
4. CloudTrail에서 루트 활동 내역 조사
5. AWS 지원 케이스 오픈 (계정 접근 불가 시)
   → https://aws.amazon.com/premiumsupport/knowledge-center/recover-compromised-account/
6. 영향받은 리소스 격리 및 피해 평가
```

---

### 4-3. AWS 커뮤니케이션 연락처

#### ⬜ ACOM-001 — AWS 계정 연락처 설정 (CIS Account.1)
**요구사항**: Billing, Operations, Security 3개 대체 연락처 설정  
**이행 방법**:
```
AWS Console → 우측 상단 계정명 → Account
→ Alternate Contacts 섹션
  - Billing: 청구 담당자 이메일/전화
  - Operations: 운영 담당자 이메일/전화
  - Security: 보안 담당자 이메일/전화
주의: 개인 이메일 말고 그룹/역할 이메일 사용 (예: security@aigendrug.com)
```
> CIS Benchmark 자동 검사 항목. 5분이면 완료 가능

---

#### ⬜ ACOM-002 — 회사 소유 연락처 정보
**요구사항**: 개인 이메일/전화가 아닌 회사 소유 연락처 사용  
**이행 방법**: ACOM-001 설정 시 함께 처리. 개인 Gmail, 개인 전화번호 사용 금지

---

### 4-4. Identity and Access Management

#### ⬜ IAM-001 — 모든 IAM 사용자 MFA 활성화 (CIS IAM.5)
**요구사항**: 콘솔 접근 가능한 모든 IAM 사용자에게 MFA 필수  
**이행 방법**:
```
1. AWS Console → IAM → Users
2. MFA 미설정 사용자 확인
3. 각 사용자 → Security credentials → MFA → Assign MFA device
   - Virtual (Google Authenticator, Authy 등)
   - Hardware (YubiKey 등)
4. MFA 미설정 시 접근 차단 정책 적용 (선택):
   조건: "Condition": {"BoolIfExists": {"aws:MultiFactorAuthPresent": "false"}}
```
> IAM Identity Center (SSO) 사용 시 SSO 레벨에서 MFA 설정하면 됨

---

#### ⬜ IAM-002 — 자격증명 정기 교체 (CIS IAM.3)
**요구사항**: IAM 액세스 키를 90일마다 교체, 미사용 키 제거  
**이행 방법**:
```
1. AWS Console → IAM → Credential Report 다운로드
   (각 사용자 액세스 키 마지막 사용일 확인)
2. 90일 이상 미사용 키 비활성화 → 30일 후 삭제
3. 새 키 생성 시 기존 키 삭제 절차 수립
4. 자동화 방법: AWS Config Rule "access-keys-rotated" 활성화
```

---

#### ⬜ IAM-003 — 강력한 비밀번호 정책 (CIS IAM.15 + IAM.16)
**요구사항**: 최소 14자 이상, 비밀번호 재사용 방지  
**이행 방법**:
```
AWS Console → IAM → Account settings → Password policy
설정값:
  - Minimum password length: 14
  - Require at least one uppercase letter: ✅
  - Require at least one number: ✅
  - Require at least one non-alphanumeric character: ✅
  - Prevent password reuse: 24회
  - Enable password expiration: 90일 (권장)
```
> CIS 자동 검사 항목 2개. 설정 즉시 PASSED

---

#### ⬜ IAM-004 — 개인별 신원 생성 (공유 계정 금지)
**요구사항**: 팀원 각자의 개별 IAM 사용자/SSO 계정 사용. 공유 admin 계정 금지  
**이행 방법**:
```
1. 현재 공유 자격증명 사용 여부 점검
2. 공유 계정 사용 중이면:
   - 개인별 IAM 사용자 또는 IAM Identity Center 계정 생성
   - 공유 계정 비활성화
3. AWS IAM Identity Center (SSO) 도입 권장 (SSO + MFA 통합 관리)
```

---

#### ⬜ IAM-005 — 제3자 접근에 IAM 역할 사용
**요구사항**: 외부 서비스/파트너에게 AWS 접근 허용 시 IAM 사용자 자격증명 공유 금지, 역할 사용  
**이행 방법**:
```
외부 서비스가 AWS 리소스에 접근해야 하는 경우:
1. IAM Role 생성 (Trust Policy에 외부 서비스 계정 ID 지정)
2. 필요한 최소 권한만 부여
3. Cross-account role 방식으로 임시 자격증명 발급
```

---

#### ⬜ IAM-006 — 최소 권한 원칙
**요구사항**: 모든 IAM 정책에서 필요한 최소한의 권한만 부여  
**이행 방법**:
```
1. AWS Console → IAM → Access Analyzer → 미사용 권한 분석
2. Policy Simulator로 실제 필요 권한 확인
3. AdministratorAccess 같은 광범위한 정책 대신 세분화된 정책 작성
4. 정기 감사: IAM Access Advisor로 마지막 서비스 접근일 확인 후 미사용 권한 제거
```

---

#### ⬜ IAM-007 — 생명주기 기반 접근 관리
**요구사항**: 퇴직/역할 변경 시 즉시 접근 권한 제거 절차 수립  
**이행 방법**:
```
온보딩/오프보딩 체크리스트 작성:
[오프보딩]
- IAM 사용자 비활성화 (즉시)
- SSO 계정 비활성화 (즉시)
- 액세스 키 삭제
- MFA 장치 제거
- 개인 소유 리소스/역할 검토

[역할 변경]
- 기존 그룹에서 제거
- 새 역할에 맞는 그룹 추가
```

---

#### ⬜ IAM-008 — 분기별 신원 감사
**요구사항**: 3개월마다 IAM 사용자/역할 목록 검토, 불필요한 신원 제거  
**이행 방법**:
```
분기 감사 항목:
1. IAM Credential Report 다운로드 → 미사용 사용자 확인
2. 더 이상 재직하지 않는 사람의 계정 확인
3. 사용되지 않는 IAM 역할 확인 (role last used 기준)
4. Cross-account 역할 중 불필요한 것 제거
5. 감사 결과 문서화 (날짜, 검토자, 조치 내역)
```

---

#### ⬜ IAM-009 — 코드에 자격증명 하드코딩 금지
**요구사항**: 소스 코드, 환경변수 파일, Git 히스토리에 AWS 자격증명 없어야 함  
**이행 방법**:
```
1. git-secrets 설치 및 훅 설정:
   brew install git-secrets
   git secrets --install
   git secrets --register-aws

2. 기존 Git 히스토리 스캔:
   git secrets --scan-history

3. CI/CD 파이프라인에 시크릿 스캔 추가 (GitHub Actions: truffleHog, gitleaks)

4. .env 파일을 .gitignore에 추가 확인
```

---

#### ⬜ IAM-010 — 시크릿 안전 저장
**요구사항**: DB 비밀번호, API 키 등 시크릿을 암호화된 전용 서비스에 저장  
**이행 방법 (AWS Secrets Manager 사용)**:
```
1. AWS Console → Secrets Manager → Store a new secret
2. 애플리케이션 코드에서 SDK로 런타임에 조회:
   python: boto3.client('secretsmanager').get_secret_value(SecretId='...')
3. EC2/ECS/Lambda의 IAM 역할에 secretsmanager:GetSecretValue 권한 부여
```
> AWS Systems Manager Parameter Store (SecureString)도 가능, 더 저렴

---

#### ⬜ IAM-011 — 고객 자격증명 암호화 및 비밀번호 해싱
**요구사항**: 고객 계정 비밀번호를 평문 저장 금지. 해싱(bcrypt, Argon2) 사용  
**이행 방법**:
```
비밀번호 저장: bcrypt, Argon2, scrypt 중 하나 사용
  python: pip install bcrypt
  hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))

대안: Amazon Cognito 사용 → 비밀번호 관리 AWS가 처리
```

---

#### ⬜ IAM-012 — 앱에서 임시 자격증명 사용
**요구사항**: EC2/Lambda/ECS에서 AWS 리소스 접근 시 IAM 역할의 임시 자격증명 사용  
**이행 방법**:
```
1. EC2: 인스턴스에 IAM 역할 연결 → 코드에서 자격증명 명시 불필요
   (AWS SDK가 Instance Metadata Service에서 자동 조회)

2. Lambda: 실행 역할(Execution Role) 설정 → 환경변수로 키 설정 금지

3. ECS/Fargate: Task Execution Role 설정

4. 확인: 코드에 boto3.Session(aws_access_key_id=...) 같은 명시적 키 없는지 점검
```

---

### 4-5. 운영 보안

#### ⬜ SECOPS-001 — 취약점 관리
**요구사항**: 의존성 및 OS 취약점 정기 스캔 및 패치 프로세스 수립  
**이행 방법**:
```
1. 컨테이너/EC2 이미지 스캔:
   - Amazon Inspector 활성화 (ECR, EC2 자동 스캔)
   - 또는 Snyk, Trivy 등 CI/CD 파이프라인에 통합

2. 의존성 스캔:
   - Python: pip-audit, Safety
   - Node.js: npm audit
   - GitHub Dependabot 활성화

3. 패치 주기 정의 (예: Critical → 48시간, High → 1주일, Medium → 1개월)

4. 패치 이력 문서화
```

---

### 4-6. 네트워크 보안

#### ⬜ NETSEC-001 — EC2 보안그룹 최소 권한 (CIS EC2.53 + EC2.54)
**요구사항**:
- 포트 22(SSH), 3389(RDP)에 0.0.0.0/0 (전체 인터넷) 허용 보안그룹 없어야 함
- 모든 VPC의 기본 보안그룹은 모든 트래픽 차단 (CIS EC2.2)

**이행 방법**:
```
1. AWS Console → EC2 → Security Groups
2. Inbound rules에 0.0.0.0/0 + 포트 22 또는 3389 조합 찾아 수정
   - SSH는 특정 IP(사무실, VPN)로 제한 or AWS Systems Manager Session Manager 사용
   - RDP 불필요 시 규칙 삭제

3. 기본 보안그룹 (default SG) 확인:
   AWS Console → VPC → Security Groups → "default" 필터
   → Inbound/Outbound 규칙 모두 삭제 (기본 SG는 사용하지 않는 것이 원칙)
```

---

#### ⬜ NETSEC-002 — 공용 서브넷 리소스 최소화
**요구사항**: 퍼블릭 서브넷에는 인터넷에서 직접 접근이 필요한 리소스만 배치  
**이행 방법**:
```
적합한 퍼블릭 서브넷 리소스:
  - ALB/NLB (로드밸런서)
  - NAT Gateway
  - Bastion Host (또는 Session Manager로 대체)

프라이빗 서브넷으로 이동해야 할 것:
  - EC2 애플리케이션 서버
  - RDS 데이터베이스
  - ECS 태스크

확인: VPC → Subnets → 각 서브넷의 Route Table에서 인터넷 게이트웨이(igw-xxx) 경로 확인
```

---

### 4-7. 백업 및 복구

#### ⬜ BAR-001 — 자동 데이터 백업 구성
**요구사항**: 모든 중요 데이터에 대한 자동 백업 설정  
**이행 방법**:
```
서비스별 백업 설정:
- RDS: 자동 백업 활성화 (보존 기간 7일 이상 권장)
  RDS → DB 인스턴스 → Modify → Backup retention period
- DynamoDB: Point-in-time Recovery (PITR) 활성화
- S3: Versioning 활성화 + S3 Replication (교차 리전)
- EBS: AWS Backup으로 스냅샷 자동화

AWS Backup 통합 관리:
  AWS Console → AWS Backup → Create backup plan → 일정 설정
```

---

#### ⬜ BAR-002 — 백업 복구 테스트
**요구사항**: 정기적으로 (최소 연 1회) 백업에서 실제 복구 테스트 수행  
**이행 방법**:
```
복구 테스트 절차 (문서화 필수):
1. 테스트 환경에 백업 복구 수행
2. 복구된 데이터 무결성 확인
3. RTO/RPO 달성 여부 측정
4. 결과 기록 (날짜, 복구 소요 시간, 담당자)
```

---

### 4-8. 탄력성 (Resilience)

#### ⬜ RES-001 — RPO 정의
**요구사항**: 데이터 손실 허용 시간(RPO) 수치 정의 및 문서화  
**이행 방법**:
```
RPO 결정 기준:
- 비즈니스 임팩트 기반으로 설정
- 예시: "최대 1시간 이내의 데이터 손실 허용"
- Self-Assessment 엑셀의 "파트너 응답" 란에 실제 수치 입력 (예: 1 hour)
```

---

#### ⬜ RES-002 — RTO 정의
**요구사항**: 서비스 복구 목표 시간(RTO) 수치 정의 및 문서화  
**이행 방법**:
```
RTO 결정 기준:
- 장애 발생 후 서비스 정상화까지 허용 시간
- 예시: "4시간 이내 서비스 복구"
- Self-Assessment 엑셀에 실제 수치 입력 (예: 4 hours)
- 아키텍처가 RTO를 달성할 수 있는지 검증 (Multi-AZ, Auto Scaling 등)
```

---

#### ⬜ RES-004 — 탄력성 테스팅
**요구사항**: 연 1회 이상 장애 시나리오 테스트 수행. FTR 승인 전 최소 1회 완료  
**이행 방법**:
```
테스트해야 할 시나리오 (아키텍처에 맞게 선택):
- AZ 장애: 특정 가용 영역 인스턴스 종료
- 인스턴스 장애: EC2 강제 종료 후 자동 복구 확인
- DB 장애 조치: RDS Multi-AZ Failover 테스트
- 네트워크 장애: 특정 서브넷 격리

AWS 도구 활용:
- AWS Fault Injection Service (FIS): 실제 장애 주입 실험
- AWS Resilience Hub: 복원력 평가 및 개선 권고

결과 문서화: 테스트 날짜, 시나리오, 관찰 결과, RTO 달성 여부
```

---

#### ⬜ RES-005 — 고객에게 탄력성 책임 고지
**요구사항**: 고객 문서/계약서에 백업 및 가용성 관련 고객 책임 명시  
**이행 방법**:
```
서비스 문서 또는 이용 약관에 포함할 내용:
- 고객이 저장한 데이터의 백업 책임 범위
- 고객이 선택 가능한 가용성 옵션 (예: 멀티리전 설정)
- 파트너가 제공하는 SLA 범위와 예외 조건
```

---

#### ⬜ RES-006 — 가용성 목표 달성 아키텍처
**요구사항**: 공개/비공개로 약속한 업타임 SLA를 실제로 달성할 수 있는 아키텍처  
**이행 방법**:
```
99.9% 가용성 목표 시 일반적 구성:
- Multi-AZ 배포 (RDS Multi-AZ, EC2 Auto Scaling across AZ)
- ALB + Auto Scaling Group
- RDS 자동 장애 조치

99.99% 이상 목표 시:
- 멀티 리전 배포
- Route 53 Health Check + Failover Routing
```

---

#### ⬜ RES-007 — 장애 시 고객 커뮤니케이션 계획
**요구사항**: 서비스 장애 발생 시 고객에게 알리는 방법과 절차 수립  
**이행 방법**:
```
커뮤니케이션 계획 수립:
1. 상태 페이지 운영 (statuspage.io, AWS Service Health Dashboard 활용)
2. 장애 탐지 → 고객 통보 기준 시간 정의 (예: 15분 이내)
3. 통보 채널: 이메일, 상태 페이지, 인앱 알림
4. 장애 종료 후 사후 보고서(Post-mortem) 제공 여부 결정

주의: AWS가 NDA 하에 제공한 정보는 고객에게 공유 금지
```

---

### 4-9. Amazon S3 버킷 접근

#### ⬜ S3-001 — S3 버킷 접근 권한 검토
**요구사항**: 모든 S3 버킷의 퍼블릭 접근 설정 검토. 불필요한 퍼블릭 버킷 없어야 함  
**이행 방법**:
```
1. AWS Console → S3 → 각 버킷의 "Permissions" 탭 확인
2. "Block all public access" 설정 확인
   - 퍼블릭 필요 없는 버킷: 모두 차단 ✅
   - 정적 웹사이트 호스팅 버킷: 최소 필요 권한만 허용

3. 계정 전체 퍼블릭 접근 차단:
   S3 → Block Public Access settings for this account → 모두 활성화

4. AWS Config Rule "s3-bucket-public-read-prohibited" 활성화 권장
```

---

### 4-10. 교차 계정 접근 (Cross-Account Access)

> 고객 AWS 계정에 직접 접근하는 기능이 없으면 전 항목 ➖ 처리 가능

#### ⬜ CAA-001 ~ CAA-007
**요구사항 요약**: 고객 AWS 계정 접근 시 IAM 자격증명 직접 수집 금지, Cross-Account Role + External ID 방식 필수  
**이행 방법**:
```
전체 구조:
[고객 계정]
  IAM Role (신뢰 정책: AIGENDRUG AWS 계정 ID + External ID 조건)
      ↓
[AIGENDRUG 계정]
  STS AssumeRole 호출 (External ID 포함) → 임시 자격증명 획득

External ID 구현:
- 고객별 UUID 생성 후 DB 저장
- 재사용 금지, 고객마다 고유값 사용
- 고객이 직접 값을 지정하는 방식 금지

고객에게 제공할 것:
- CloudFormation 템플릿 (역할 자동 생성용, 최소 권한 정책 포함)
- 역할 ARN 입력 UI
```

---

### 4-11. 민감한 데이터

#### ⬜ SDAT-001 — 민감 데이터 식별
**요구사항**: 처리하는 PII, PHI 등 민감 데이터 목록화  
**이행 방법**:
```
데이터 분류 작업:
1. 시스템에서 수집/저장하는 모든 데이터 목록 작성
2. 민감도 분류: Public / Internal / Confidential / Restricted
3. PII 해당 여부 확인:
   - 이름, 이메일, 전화번호, 주소 → PII
   - 건강 정보 → PHI
   - 결제 정보 → PCI 범위
4. Amazon Macie 활성화 (S3의 PII 자동 탐지)
```

---

#### ⬜ SDAT-002 — 저장 데이터 암호화
**요구사항**: 민감 데이터가 저장된 모든 스토리지 암호화  
**이행 방법**:
```
서비스별 암호화 설정:
- S3: 버킷 기본 암호화 활성화 (SSE-S3 또는 SSE-KMS)
- RDS: 스토리지 암호화 활성화 (DB 생성 시 설정, 이후 변경 어려움)
- EBS: 볼륨 암호화 (계정 기본값으로 설정 가능)
  EC2 → Settings → EBS encryption → Enable

KMS 키 관리:
  AWS KMS → Customer managed keys → 서비스별 키 생성 권장
```

---

#### ⬜ SDAT-003 — 전송 중 암호화
**요구사항**: VPC 외부로 민감 데이터 전송 시 TLS 등 암호화 프로토콜 사용  
**이행 방법**:
```
확인 사항:
- API 엔드포인트: HTTPS (TLS 1.2 이상) 강제
- ALB → HTTP 리스너를 HTTPS로 리다이렉트 설정
- 내부 서비스 간 통신도 가능하면 TLS 적용
- ACM (AWS Certificate Manager)으로 SSL 인증서 무료 발급

HTTP 접근 차단 방법:
  ALB → Listener (port 80) → Default action: Redirect to HTTPS
```

---

### 4-12. 규제 준수

#### ⬜ RCVP-001 — 컴플라이언스 표준 준수 프로세스
**요구사항**: 제품이 준수한다고 광고하는 컴플라이언스 표준의 실제 충족 프로세스 수립  
**이행 방법**:
```
AIGENDRUG 적용 가능 표준 확인:
- 의료 데이터 처리: HIPAA
- 금융 데이터 처리: PCI DSS
- EU 사용자: GDPR
- 국내: 개인정보보호법, ISMS-P

프로세스 수립:
1. 적용 표준 목록 작성
2. 각 표준별 요구사항 매핑
3. 정기 준수 점검 일정 수립 (연 1회 이상)
4. 결과 문서화
```

---

## 5. CIS Benchmark 리포트 생성

### 절차
```
1. AWS Console → Security Hub → Go to Security Hub 활성화
   (사전 조건: AWS Config 활성화 필요)

2. Standards 탭 → "CIS AWS Foundations Benchmark v3.0" 활성화

3. 수 시간 대기 (첫 스캔 완료까지)

4. Security standards → CIS → View results
   → 필수 8개 항목 모두 Passed 확인

5. Download 버튼 (CSV) 클릭 → 저장
   → 모든 프로덕션 계정 + 리전별로 반복

6. docs/ 폴더에 저장 후 FTR 제출 시 업로드
```

### 필수 통과 8개 항목
| 항목 | 빠른 조치 방법 |
|---|---|
| IAM.4 (root 액세스 키 없음) | Security Credentials → 키 삭제 |
| IAM.5 (콘솔 접근 유저 MFA) | IAM Users → MFA 활성화 |
| IAM.3 (정적 자격증명 모니터링) | 90일 이상 미교체 키 교체 |
| EC2.54 + EC2.53 (보안그룹 최소 권한) | 0.0.0.0/0 + SSH/RDP 인바운드 제거 |
| IAM.15 (비밀번호 14자 이상) | IAM Account settings → 정책 수정 |
| IAM.16 (비밀번호 재사용 방지) | IAM Account settings → 재사용 제한 |
| EC2.2 (기본 SG 전체 트래픽 차단) | default SG → 인바운드/아웃바운드 규칙 삭제 |
| Account.1 (계정 연락처 설정) | Account → Alternate Contacts 설정 |

---

## 6. FTR 신청 절차

> 현재 일시 중단(Paused). 아래 절차는 재개 후 진행

```
1. Partner Central 로그인
   https://partnercentral.awspartner.com

2. Build → Solutions → FTR 대상 솔루션 선택 → View Details

3. "Request Validation" 섹션
   - FTR Checklist: Self-Assessment 엑셀 업로드
   - Security Tool Report: CIS Benchmark CSV 업로드
   - Architecture Diagram: png/jpeg 업로드

4. Request Validation 버튼 클릭

5. 결과:
   - 자동 승인 (30분): CIS 리포트 + Architecture Diagram 제출 + 모든 항목 충족 시
   - PSA 수동 검토: CIS 리포트 없거나 항목 미충족 시 → 이메일로 연락

6. 피드백 수신 시 6개월 이내 수정 후 재제출
```

---

## 7. 심사 이후 프로세스

### 승인 시
- FTR 상태: **Approved** (3년 유효)
- Software Path → **Validated** 단계 진입
- 혜택 활성화: AWS Partner Badge, Partner Solution Finder 등재, ISV Accelerate 신청 가능

### 수정 요청 시
- PSA가 이메일로 미충족 항목 목록 + 가이드 제공
- 수정 후 PSA에 확인 메일 발송 → 재승인
- 6개월 내 미완료 시 신규 신청 필요 (최신 체크리스트 기준 적용)

### 만료 및 갱신
- 만료 90/60/30일 전 Alliance Lead에게 이메일 알림
- 갱신 시 당시 최신 체크리스트로 전체 재제출 (이전 서류 재활용 불가)
- 만료 90일 전 갱신 시작 권장

---

## 8. 단축 경로

### WAFR 면제
- **조건**: 최근 12개월 내 AWS 직원 또는 WAPP 파트너 수행 WAFR 완료 + Security/Reliability/OE 필라 HRI 0건
- **제출**: WAFR 리포트 + HOST-001, SUP-001, WAFR-001, WAFR-002, Cross Account Access 5개 항목 자가진단
- **활용 체크리스트**: [FTR Alternative Checklist](https://apn-checklists.s3.amazonaws.com/foundational/partner-hosted/partner-hosted-alternative/CwYryx6XW.html)

### SOC 2 Type II
- **조건**: 현재 유효 + unqualified opinion + AWS in scope + 해당 솔루션 in scope + Security & Availability trust center 포함
- **효과**: 45개 항목 → **11개로 단축**
- **제출**: SOC 2 Type II 리포트 + Alternative 체크리스트 + CIS 리포트 + Architecture Diagram

---

## 9. FTR 이후 — Software Path Validated 혜택

FTR 승인으로 Validated 단계 진입 시 활성화되는 혜택:

| 혜택 | 설명 |
|---|---|
| AWS Partner Badge | 파트너 배지 (웹사이트, 마케팅 자료에 사용) |
| Partner Solution Finder 등재 | AWS.com의 파트너 솔루션 디렉토리 노출 |
| Partner Discovery Portal | AWS 내부 영업팀이 파트너 솔루션 검색 가능 |
| ISV Accelerate | AWS와 공동 영업(Co-sell) 프로그램 신청 가능 |
| ACE Referrals | AWS로부터 고객 기회 추천 수신 가능 |
| Qualified Software 배지 | 솔루션에 FTR 인증 배지 표시 |
| POA Funding | Partner Opportunity Acceleration 펀딩 신청 가능 |
| Well-Architected Partner Program 신청 가능 | |
| ISV Workload Migration Program 신청 가능 | |

---

## 참고 링크

| 자료 | URL |
|---|---|
| FTR 공식 페이지 | https://aws.amazon.com/ko/partners/foundational-technical-review/ |
| Software Path 단계별 상세 | https://partnercentral.awspartner.com/partnercentral2/s/partnerpathdetails?partnerPath=ISV |
| FTR 체크리스트 (한국어) | https://apn-checklists.s3.amazonaws.com/foundational/partner-hosted/partner-hosted/ko/CVLHEC5X7.html |
| FTR Alternative 체크리스트 | https://apn-checklists.s3.amazonaws.com/foundational/partner-hosted/partner-hosted-alternative/CwYryx6XW.html |
| Self-Assessment 엑셀 | https://apn-checklists.s3.amazonaws.com/foundational/partner-hosted/partner-hosted/CVLHEC5X7/Partner%20Hosted%20Foundational%20Technical%20Review%20Self-Assessment.xlsx |
| CIS → Security Hub 매핑 | https://docs.aws.amazon.com/securityhub/latest/userguide/cis-aws-foundations-benchmark.html |
| AWS Well-Architected Tool | https://console.aws.amazon.com/wellarchitected |
| AWS Backup | https://console.aws.amazon.com/backup |
| AWS Fault Injection Service | https://console.aws.amazon.com/fis |
