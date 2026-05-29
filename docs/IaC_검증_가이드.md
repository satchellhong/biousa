# IaC 기반 FTR 검증 가이드

> **주의**: 검증 도구는 IaC 코드를 **읽기 전용**으로 파싱합니다.
> `terraform apply`, AWS CLI 리소스 조작, `.tf` 파일 수정은 절대 수행하지 않습니다.

---

## 개요

`src/tools/iac_validator.py` 가 `iac/DrugVLAB_Django_Infra/` 아래 **모든 `.tf` 파일**(루트 + 모듈 내부 220개+)을 재귀 파싱하여 FTR 공식 ID 기준 **46개 항목**에 대해 PASS / FAIL / WARN / MANUAL 판정을 반환합니다.

### 판정 기준

| 상태 | 의미 | 조치 |
|---|---|---|
| ✅ PASS | IaC에서 요건 충족 확인 | 없음 |
| ❌ FAIL | 요건 미충족 — IaC 수정 필요 | `.tf` 파일 수정 후 재검증 |
| ⚠️ WARN | 부분 충족 또는 확인 불완전 | 세부 검토 후 PASS/FAIL 판단 |
| ⬜ MANUAL | IaC로 판정 불가 | 아래 체크리스트 참고하여 콘솔 확인 |

### 검증 항목 (IaC 자동 검증 가능)

| 항목 ID | 검증 내용 | 검사 패턴 |
|---|---|---|
| IAM-005 | 제3자 접근에 IAM 역할 사용 | `identity_access_iam` 모듈 존재 여부 |
| IAM-006 | 최소 권한 원칙 | `AdministratorAccess` / `PowerUserAccess` 관리형 정책 참조 없음 |
| IAM-009 | 코드에 자격증명 하드코딩 금지 | `AKIA[A-Z0-9]{16}` 패턴, `secret_access_key = "..."` 직접 할당 없음 |
| IAM-010 | 시크릿 Secrets Manager 저장 | `secrets_manager`, `discovery_ssm` 모듈 존재 여부 |
| IAM-012 | 앱에서 임시 자격증명 사용 | `identity_access_iam` 모듈 존재 여부 |
| NETSEC-001 | 보안그룹 최소 권한 | ① `0.0.0.0/0` + `protocol="-1"` ingress 조합 없음 ② `allow_ssh=false` prod 조건 |
| BAR-001 | 자동 백업 구성 | ① DynamoDB `point_in_time_recovery`/`pitr_enabled=true` ② S3 `status="Enabled"` 또는 삼항식+파라미터 |
| RES-006 | 업타임 SLA 달성 아키텍처 | ① 변수 파일 복수 AZ 정의 ② `load_balancer_alb` 모듈 존재 |
| S3-001 | S3 버킷 접근 권한 | ① `public_access_block` 4개 파라미터 all true ② `DenyInsecureTransport` 정책 ③ `sse_algorithm` 설정 |
| SDAT-002 | 저장 데이터 암호화 | ① DynamoDB SSE ② S3 SSE-KMS/AES256 ③ `aws_kms_key enable_key_rotation=true` |
| SDAT-003 | 전송 중 암호화 | ① `generic_acm` + `load_balancer_alb` 모듈 ② S3 `DenyInsecureTransport` |

---

## 수동 실행 방법

### 방법 1 — Python 직접 실행 (권장)

```bash
conda activate aws_ftr
cd /Users/schong/aws_ftr

python -c "
from src.tools.iac_validator import validate_iac
r = validate_iac()
print('검증 결과:', r['summary'])
for x in r['results']:
    icon = {'PASS':'✅','FAIL':'❌','WARN':'⚠️','MANUAL':'⬜'}[x['status']]
    print(f'{icon} {x[\"id\"]}: {x[\"name\"]}')
    for e in x['evidence']: print(f'   → {e}')
"
```

### 방법 2 — 마크다운 리포트 파일 출력

```bash
conda activate aws_ftr
cd /Users/schong/aws_ftr

python -c "
import datetime
from src.tools.iac_validator import validate_iac
from src.tools.report_generator import generate_report
r = validate_iac()
today = datetime.datetime.now().strftime('%Y-%m-%d')
path = f'docs/IaC_검증_리포트_{today}.md'
generate_report(r, path)
print('저장 완료:', path)
print('요약:', r['summary'])
"
```

### 방법 3 — MCP 툴 호출 (Claude Code에서)

```
ftr_validate_iac()              # 검증만
ftr_generate_report()           # 검증 + 리포트 파일 저장
ftr_validate_and_update()       # 검증 + PASS 항목 자동으로 progress 업데이트
```

### 방법 4 — 다른 IaC 디렉터리 지정

```bash
python -c "
from src.tools.iac_validator import validate_iac
r = validate_iac('/path/to/other/terraform/dir')
print(r['summary'])
"
```

---

## MANUAL 항목 수동 확인 체크리스트

IaC로 판정 불가한 35개 항목은 AWS 콘솔 또는 문서로 직접 확인합니다.

### 사전 요구사항

| 항목 ID | 항목 | 확인 위치 | 확인 방법 |
|---|---|---|---|
| CIS | CIS Benchmark 리포트 | AWS Security Hub | Security Hub → Compliance → CIS AWS Foundations |
| GA | 솔루션 GA 상태 | Partner Central | 솔루션이 실제 판매/제공 중인지 확인 |
| HOST-001 | 호스팅 모델 | 내부 확인 | 모든 핵심 컴포넌트가 AWS에서 실행되는지 확인 + Architecture Diagram 작성 |
| SUP-001 | Business Support | AWS Console | 우측 상단 계정 → Support → Support Plans |
| WAFR-001 | 연간 아키텍처 검토 | Well-Architected Tool | AWS Console → Well-Architected Tool → 검토 수행 |
| WAFR-002 | 공동 책임 모델 검토 | 내부 문서 | AWS 공동 책임 모델 검토 및 문서화 |

### 루트 계정

| 항목 ID | 항목 | 확인 위치 | 확인 방법 |
|---|---|---|---|
| ARC-001 | 루트 사용자 예외적 사용 | IAM 콘솔 | IAM → Security Credentials → 루트 최근 로그인 이력 없음 |
| ARC-004 | 루트 액세스 키 없음 | IAM 콘솔 | IAM → Security Credentials → Access keys (root) = 없음 |
| ARC-005 | 루트 침해 IR 런북 | 내부 문서 | 루트 계정 침해 대응 절차 문서 작성 |

### AWS 커뮤니케이션

| 항목 ID | 항목 | 확인 위치 | 확인 방법 |
|---|---|---|---|
| ACOM-001 | 계정 연락처 3개 설정 | Account 설정 | Account → Alternate Contacts (Billing/Operations/Security) |
| ACOM-002 | 회사 소유 연락처 사용 | Account 설정 | 개인 이메일/전화 아닌 그룹 이메일 사용 여부 |

### IAM

| 항목 ID | 항목 | 확인 위치 | 확인 방법 |
|---|---|---|---|
| IAM-001 | 모든 IAM 사용자 MFA | IAM 콘솔 | IAM → Users → 각 유저 MFA device 등록 여부 |
| IAM-002 | 자격증명 90일 교체 | IAM 콘솔 | IAM → Credential Report → 마지막 키 교체일 확인 |
| IAM-003 | 비밀번호 정책 14자+재사용방지 | IAM 콘솔 | IAM → Account settings → Password policy |
| IAM-004 | 개인별 신원 / 공유 계정 금지 | IAM 콘솔 | IAM → Users 목록에서 공유 계정 없는지 확인 |
| IAM-007 | 생명주기 기반 접근 관리 | 내부 문서 | 온보딩/오프보딩 체크리스트 존재 여부 |
| IAM-008 | 분기별 신원 감사 | 내부 문서 | 감사 일정 및 최근 감사 기록 |
| IAM-011 | 고객 자격증명 암호화/해싱 | 앱 코드 | 비밀번호 해싱(bcrypt/Argon2) 또는 Cognito 사용 여부 |

### 운영 보안 / 네트워크

| 항목 ID | 항목 | 확인 위치 | 확인 방법 |
|---|---|---|---|
| SECOPS-001 | 취약점 관리 프로세스 | 내부 문서 | Amazon Inspector/Snyk 등 스캔 도구 + 패치 주기 정책 |
| NETSEC-002 | 기본 VPC SG 잠금 | VPC 콘솔 | VPC → Security Groups → default → inbound/outbound 규칙 없음 |

### 백업 / 탄력성

| 항목 ID | 항목 | 확인 위치 | 확인 방법 |
|---|---|---|---|
| BAR-002 | 백업 복구 테스트 | 내부 문서 | 연 1회 이상 복구 테스트 기록 (날짜, 소요 시간, 결과) |
| RES-001 | RPO 정의 | 내부 문서 | DR/런북 문서에 RPO 수치 명시 (예: 1 hour) |
| RES-002 | RTO 정의 | 내부 문서 | DR/런북 문서에 RTO 수치 명시 (예: 4 hours) |
| RES-004 | 탄력성 테스팅 | 내부 문서 | 장애 주입 테스트 기록 (AWS FIS 활용 권장) |
| RES-005 | 탄력성 책임 고지 | 서비스 약관 | SLA 문서에 고객 책임 범위 명시 여부 |
| RES-007 | 장애 시 커뮤니케이션 계획 | 내부 문서 | 장애 탐지 → 고객 통보 기준 시간 및 채널 정의 |

### Cross-Account (고객 AWS 계정 접근 없으면 전 항목 ➖)

| 항목 ID | 항목 | 확인 방법 |
|---|---|---|
| CAA-001 | Cross-Account Role 사용 | 고객 계정 접근 구조에서 IAM 사용자 키 공유 없이 Role 사용 |
| CAA-002 | External ID / Issuer URL 사용 | Cross-Account Role Trust Policy에 External ID 조건 확인 |
| CAA-003 | 고객 제공 자격증명 폐기 | 과거 고객이 준 IAM 키 사용 여부 없는지 확인 |
| CAA-004 | External ID 자체 생성 | External ID를 고객이 아닌 파트너(AIGENDRUG)가 UUID 생성 |
| CAA-005 | External ID 고유성 | 고객별 External ID가 중복 없이 고유한지 확인 |
| CAA-006 | External ID 읽기 전용 고객 제공 | 고객이 자신의 External ID를 조회할 수 있는 방법 제공 여부 |
| CAA-007 | 자동 설정 메커니즘 | CloudFormation 템플릿 등 고객 계정 설정 자동화 가이드 제공 여부 |

### 민감 데이터 / 규제

| 항목 ID | 항목 | 확인 위치 | 확인 방법 |
|---|---|---|---|
| SDAT-001 | 민감 데이터 식별 | 내부 문서 | PII/PHI 등 처리 데이터 목록 + 민감도 분류 문서 |
| RCVP-001 | 컴플라이언스 준수 프로세스 | 내부 문서 | 적용 컴플라이언스 표준(HIPAA, GDPR 등) + 준수 점검 프로세스 |

---

## 재검증 방법

```bash
conda activate aws_ftr
cd /Users/schong/aws_ftr

# 요약만 확인
python -c "from src.tools.iac_validator import validate_iac; r=validate_iac(); print(r['summary'])"

# 리포트 재생성
python -c "
import datetime
from src.tools.iac_validator import validate_iac
from src.tools.report_generator import generate_report
r = validate_iac()
today = datetime.datetime.now().strftime('%Y-%m-%d')
generate_report(r, f'docs/IaC_검증_리포트_{today}.md')
"
```

또는 MCP 툴: `ftr_validate_iac()` / `ftr_generate_report()`
