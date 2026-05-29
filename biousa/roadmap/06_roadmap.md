# DrugVLAB — 6개월 로드맵

## 전제

- 기존 플랫폼(인프라·인증·크레딧·워크플로우 실행)은 변경 없음
- 추가되는 것: Review workflow + 화면 개선 + Export
- 백엔드 1명 / 프론트엔드 1명 기준

---

## Phase 1 — Review 기반 (Month 1–2)

**목표**: "결과 확인 → 판정 → 기록" 흐름 완성

### 백엔드
- `review` 앱 신규 생성
  - `POST /api/review/submit/` — go/hold/no-go + memo 저장
  - `GET /api/review/get/` — 특정 라이브러리의 review 조회
  - `GET /api/review/list/` — 그룹 내 review 목록 (필터: decision, workflow)
- DynamoDB: `dir_type: REVIEW` 레코드 구조 정의
- `WorkflowStatusView` 응답에 `review_status` 필드 추가
- Cognito `custom:role` attribute 추가
  - `POST /api/auth/role/grant/`
  - `POST /api/auth/role/revoke/`
  - `GET /api/auth/role/me/`

### 프론트엔드
- 결과 상세 화면 공통: **Review Panel** 추가
  - go/hold/no-go 선택 + memo + suggested next experiment
  - reviewer role 없으면 read-only
- `AdminPage.tsx`: Role 컬럼 + grant/revoke UI
- `MyInfo.tsx`: 현재 role 표시

### 완료 기준
- reviewer가 결과 화면에서 판정을 남기고 저장할 수 있다
- 동일 화면에서 이전 review 이력을 볼 수 있다

---

## Phase 2 — Review 운영 화면 (Month 2–3)

**목표**: reviewer의 일상 운영 흐름 지원

### 백엔드
- `POST /api/review/request/` — researcher가 reviewer에게 검토 요청
- Pending 상태 관리 (요청됨 / 검토완료)

### 프론트엔드
- **`ReviewListPage.tsx`** 신규 (메뉴: Review)
  - Pending Reviews 탭: 검토 대기 목록
  - Decision History 탭: 전체 판정 이력, 필터(go/hold/no-go/workflow/date)
- **Portfolio 화면 개선**
  - Pending Review 카운트 badge
  - 최근 decision history 5건

### 완료 기준
- reviewer가 Pending Reviews 목록에서 바로 결과 화면으로 이동할 수 있다
- Decision History에서 필터로 원하는 결과를 빠르게 찾을 수 있다

---

## Phase 3 — Evidence 표시 강화 (Month 3–4)

**목표**: 결과 화면이 "분석 결과 dump"가 아니라 "검토 가능한 근거 패키지"로 보이게

### 프론트엔드
- **Recommendation Card** 컴포넌트 신규
  - predicted response + confidence + rank + vs. reference drug
  - 기존 ranking 결과를 카드 형태로 재구성

- **Evidence Panel** 컴포넌트 신규 (Mechanism Lens 시각화)
  - CSG2A: similar known drugs, MoA alignment, top pathways
  - Docking/PLIP: key interactions summary
  - 기존 결과 파일에서 데이터 파싱

- **Context Panel** 컴포넌트 신규 (Clinical만)
  - THERAPI: nearest cell lines, tissue consistency, heterogeneity score
  - 기존 clinical 결과 파일에서 파싱

### 백엔드
- 결과 파일(EFS)에서 Evidence/Context 요약 데이터를 structured JSON으로 추출하는 utility 추가
- `WorkflowResultFileRetrieveView` 응답에 summary field 추가 (옵션)

### 완료 기준
- 결과 화면에서 Recommendation Card + Evidence Panel + Review Panel이 한 화면에 보인다
- reviewer가 별도 파일을 열지 않고도 판정에 필요한 근거를 화면에서 확인할 수 있다

---

## Phase 4 — Export & 정리 (Month 4–5)

**목표**: 회의에 바로 올릴 수 있는 artifact 생성

### 백엔드
- `POST /api/export/report/` — Decision Card JSON 생성
  - 결과 summary + review record + evidence summary 결합
  - 응답: structured JSON
- (선택) Lambda 기반 PDF 생성 or 프론트에서 JSON → PDF 렌더링

### 프론트엔드
- 결과 화면 / Review 완료 후 "Export Decision Card" 버튼
- JSON 다운로드 (v1)
- 브라우저 print-to-PDF 또는 서버 PDF (v2)

### 완료 기준
- reviewer가 판정 완료 후 회의용 Decision Card를 1클릭으로 내려받을 수 있다

---

## Phase 5 — 안정화 및 FTR 대응 (Month 5–6)

**목표**: AWS FTR 통과 + 첫 enterprise 고객 온보딩 준비

### 작업 항목
- Review/Export API 전체 테스트 케이스 작성 (기존 test_case 패턴 적용)
- Audit trail 확인: CloudTrail + `audit-activity-ddb`가 review 행위를 커버하는지 검증
- RBAC 엣지 케이스 처리 (역할 없는 사용자, 그룹 없는 사용자 등)
- Private Runtime 배포 가이드 문서화
- 성능 검증: 대용량 결과 파일 parsing, DynamoDB scan 최적화

---

## 타임라인 요약

```
Month 1    Month 2    Month 3    Month 4    Month 5    Month 6
┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
│ Phase 1  │ Phase 1  │ Phase 2  │ Phase 3  │ Phase 4  │ Phase 5  │
│ Review   │ ↓        │ Review   │ Evidence │ Export   │ FTR /    │
│ backend  │ Review   │ 운영화면  │ 표시강화  │ Decision │ 안정화   │
│ + role   │ Panel FE │          │          │ Card     │          │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
```

---

## 건드리지 않는 것

- 워크플로우 실행 로직 전체 (Nextflow + AWS Batch)
- 크레딧/과금 시스템 (billing-engine 모듈)
- 라이브러리/그룹 CRUD
- Terraform 인프라 모듈
- Cognito 인증 흐름 (`is_admin` 포함)
- 기존 결과 파일 형식 (EFS 경로, 파일 포맷)
