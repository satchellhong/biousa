# AWS FTR 인증 준비 도구

DrugVLAB 인프라(Partner Hosted on AWS)의 AWS FTR(Foundational Technical Review) 인증을 위한 MCP 서버 및 IaC 자동 검증 도구입니다.

---

## 빠른 시작 — 검증 순서

### 1단계: 환경 준비

```bash
conda activate aws_ftr
cd /Users/schong/aws_ftr
```

### 2단계: 통합 점검 실행 (IaC + AWS 계정)

IaC 코드 분석과 boto3 계정 점검을 한 번에 실행합니다.

```bash
python -c "
import datetime
from src.tools.iac_validator import validate_iac
from src.tools.console_checker import check_console
from src.tools.report_generator import generate_full_report
today = datetime.datetime.now().strftime('%Y-%m-%d')
generate_full_report(validate_iac(), check_console(), f'docs/FTR_통합_리포트_{today}.md')
print('완료')
"
```

두 가지를 동시에 점검합니다:
- **IaC 자동 검증**: `iac/DrugVLAB_Django_Infra/` 220개 `.tf` 파일 읽기 전용 파싱 → 46개 FTR 항목 판정
- **콘솔 자동 점검**: boto3 읽기 전용 API로 실제 AWS 계정 상태 확인 → 10개 항목 판정

**결과 해석:**

| 상태 | 의미 |
|---|---|
| ✅ PASS | 요건 충족 확인됨 |
| ❌ FAIL | 요건 미충족 — 조치 필요 |
| ⚠️ WARN | 부분 충족 또는 확인 불완전 — 세부 검토 필요 |
| ⬜ MANUAL | 자동 판정 불가 — 콘솔/문서 직접 확인 필요 |

### 3단계: 리포트 확인 및 FAIL 항목 조치

`docs/FTR_통합_리포트_YYYY-MM-DD.md` 열어서 ❌ 항목 확인 후 순서대로 조치합니다.

상세 이행 방법은 [docs/FTR_상세_절차.md](docs/FTR_상세_절차.md) 참고.

### 4단계: 수동 확인 필요 항목 처리

리포트의 ⬜ MANUAL 항목은 [docs/IaC_검증_가이드.md](docs/IaC_검증_가이드.md)의 체크리스트 참고.

### 5단계: FTR 신청

[docs/FTR_상세_절차.md](docs/FTR_상세_절차.md) 참고. Partner Central에서 제출 서류:
1. FTR Self-Assessment 엑셀 (46개 항목 모두 완료)
2. CIS AWS Foundations Benchmark 리포트 (AWS Security Hub)
3. Architecture Diagram (jpeg/png)

---

## 현재 점검 결과 (2026-04-29 기준)

[docs/FTR_통합_리포트_2026-04-29.md](docs/FTR_통합_리포트_2026-04-29.md) 참고.

**IaC(46개) + 콘솔(10개) 병합 기준 총 47개 항목:**

| 점검 유형 | PASS | FAIL | WARN | MANUAL | 합계 |
|---|---|---|---|---|---|
| 🏗️ IaC 자동 검증 | 11 | 0 | 0 | 35 | 46 |
| 🔍 콘솔 자동 점검 | 1 | 9 | 0 | 0 | 10 |
| **병합 통합** | **12** | **9** | **0** | **26** | **47** |

### ❌ 즉시 조치 필요 항목 (9건)

| 항목 | 문제 | 조치 방법 |
|---|---|---|
| ARC-004 | 루트 액세스 키 1개 존재 | IAM → Security Credentials → Access keys → Delete |
| ACOM-001 | 계정 연락처 3개 모두 미설정 | Account → Alternate Contacts에 Billing/Operations/Security 설정 |
| IAM-001 | MFA 미설정 사용자 5명 (hyerinkim, seokcholhong, sugyunan, tester, youngkukkim) | IAM → Users → Security credentials → MFA 할당 |
| IAM-002 | 90일 초과 액세스 키 8개 (최대 1167일) | IAM → Credential Report → 오래된 키 교체 또는 비활성화 |
| IAM-003 | 비밀번호 정책 미설정 | IAM → Account settings → Password policy 설정 (14자+, 재사용방지) |
| NETSEC-002 | 3개 VPC 기본 SG 모두 규칙 존재 | VPC → Security Groups → default → 인바운드/아웃바운드 규칙 삭제 |
| OPS | CloudTrail trail 없음 | CloudTrail → Create trail (멀티리전, 파일 검증 활성화) |
| CIS | Security Hub 비활성화 | Security Hub → Enable → CIS AWS Foundations Benchmark 활성화 |
| SUP-001 | Basic Support (Business 필요) | Support → Support Plans → Business 선택 |

### ✅ PASS 항목 (12건)

**IaC 검증 (11건):** IAM-005(IAM Role 기반 접근), IAM-006(최소 권한), IAM-009(하드코딩 없음), IAM-010(Secrets Manager), IAM-012(임시 자격증명), NETSEC-001(보안그룹 최소권한), BAR-001(DynamoDB PITR + S3 버전관리), RES-006(멀티-AZ + ALB), S3-001(퍼블릭차단+HTTPS-only+암호화), SDAT-002(저장암호화+KMS rotation), SDAT-003(TLS)

**콘솔 점검 (1건):** ARC-001(루트 MFA 활성화)

상세 근거는 [docs/IaC_검증_리포트_2026-04-29.md](docs/IaC_검증_리포트_2026-04-29.md) 참고.

### ⬜ 수동 확인 필요 (26건)

문서 작성, 내부 프로세스 수립, 또는 앱 코드 레벨 확인이 필요한 항목. 상세 체크리스트는 [docs/IaC_검증_가이드.md](docs/IaC_검증_가이드.md) 참고.

---

## 프로젝트 구조

```
aws_ftr/
├── src/
│   ├── server.py               # FastMCP 서버 (MCP 툴 등록)
│   └── tools/
│       ├── iac_validator.py    # IaC 검증 (220개 .tf 읽기 전용 파싱, 46개 FTR 항목)
│       ├── console_checker.py  # boto3 계정 점검 (읽기 전용, 10개 항목)
│       ├── report_generator.py # IaC 단독 / IaC+콘솔 통합 리포트 생성
│       ├── checklist.py        # FTR 체크리스트 파싱/캐싱
│       ├── progress.py         # 항목 상태/증거 관리
│       └── browser.py          # camofox 브라우저 REST API 래퍼
├── iac/
│   └── DrugVLAB_Django_Infra/  # 검증 대상 Terraform 코드 (읽기 전용)
├── docs/
│   ├── FTR_상세_절차.md        # FTR 전체 절차 + 항목별 이행 방법 (자동 점검 결과 반영)
│   ├── IaC_검증_가이드.md      # 실행 방법 + MANUAL 체크리스트
│   ├── IaC_검증_리포트_*.md    # IaC 단독 검증 리포트 (자동 생성)
│   └── FTR_통합_리포트_*.md    # IaC + 콘솔 통합 리포트 (자동 생성) ← 주요 사용
└── .mcp.json                   # Claude Code MCP 서버 등록
```

---

## 개발 환경

```bash
conda create -n aws_ftr python=3.11
conda activate aws_ftr
pip install -r requirements.txt
```

Python 경로: `/Users/schong/miniconda/envs/aws_ftr/bin/python`

## MCP 서버 실행

```bash
# MCP 서버 (stdio — Claude Code에서 자동 실행)
cd /Users/schong/aws_ftr
/Users/schong/miniconda/envs/aws_ftr/bin/python src/server.py
```

Claude Code에서 사용 가능한 MCP 툴:
- `ftr_full_report()` — **IaC + 콘솔 통합 점검 + 리포트 저장** (주 사용)
- `ftr_validate_iac()` — IaC 검증만
- `ftr_check_console()` — boto3 콘솔 점검만
- `ftr_generate_report()` — IaC 단독 리포트 저장
- `ftr_validate_and_update()` — IaC 검증 + PASS 항목 자동 완료 처리
- `ftr_get_checklist()` — 체크리스트 조회
- `ftr_get_summary()` — 진행 현황 요약

## 공식 문서

- [FTR 체크리스트 (영문)](https://apn-checklists.s3.amazonaws.com/foundational/partner-hosted/partner-hosted/CVLHEC5X7.html)
- [FTR 체크리스트 (한국어)](https://apn-checklists.s3.amazonaws.com/foundational/partner-hosted/partner-hosted/ko/CVLHEC5X7.html)
- [FTR 가이드 PDF](./docs/AWS_FTR_Guide_latest.pdf)
- [FTR 공식 페이지](https://aws.amazon.com/ko/partners/foundational-technical-review/)
