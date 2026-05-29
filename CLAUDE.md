# BIO USA 2026 — 파트너 탐색 지침

---

## 회사 현황 — AigenDrug (아이겐드럭)

**한 줄 정의**: 의약화학자-in-the-Loop 기반 AI 신약개발 플랫폼 (DrugVLAB™)
**핵심 문제의식**: 기존 AI 신약개발 툴은 Black-box + 데이터 외부유출 + 피드백 재학습 불가 → DrugVLAB은 이 3가지를 해결

**매출 추이**
| 연도 | 기업 매출 | 정부출연금 | 총계 |
|---|---|---|---|
| 2023 | 3.3억 | 1.5억 | 4.8억 |
| 2024 | 4.1억 | 4.4억 | 8.5억 |
| 2025 | 3.3억 | 7.0억 | 10.3억 |

**매출 목표**: 2026 5억 → 2027 20억 → 2028 40억

**기존 고객사**: GC녹십자, 한미약품, 대웅제약, 아모레퍼시픽, 서울대병원, 이화여대, 서울대, 나무ICT
**DrugVLAB 사용 기관**: 이화여대, 건국대, 중앙대

---

## BM 선순환 구조 (핵심)

```
연구용역 ──고도화──▶ SaaS (DrugVLAB)
    │    ◀──효율화──     │
    │                   │
    └────자산화────▶ 신약후보물질 IP ◀────자산화────┘
                  (기술이전·라이선스)
```

- **연구용역** (단기, 현재 4개 진행중 → 5개 추가): 제약·바이오텍·화장품사 프로젝트, 건당 0.5~2억
- **SaaS DrugVLAB** (중장기, 현재 3종 → 10종 추가): 구독제·크레딧 과금, 커스텀 모델 구축
- **신약후보물질 IP** (장기, 현재 5개 파이프라인 → 10개): 기술이전 Upfront/Milestone/Royalty

---

## DrugVLAB 플랫폼 — 3모듈 구조

| 모듈 | 기능 | 레퍼런스 고객 | 상태 |
|---|---|---|---|
| **ChemGen™** | Human-in-the-Loop 화합물 생성 (PPI/Kinase inhibitor) | 대웅제약, 이화여대, GC녹십자 | ✅ Operational |
| **ChemResponse™** | 세포주 → 환자 수준 약물반응성 예측 (CSG2A + THERAPI + PertDA) | 한미약품, 한국생명공학연구원 | ✅ Operational |
| **ChemTox™** | 독성·부작용 검증 (간독성, 장기독성, ADME) | 목암생명과학연구소, 서울대병원, 국가독성과학연구소 | 🔜 2026 하반기 |

**기술 차별점**
- Medicinal Chemist-in-the-Loop: 실험 피드백 → AI 재학습 → 라운드별 정확도 향상
- No-data-egress: 고객 AWS VPC 배포, 핵심 화합물 데이터 외부 유출 없음
- AUROC 0.757 (TCGA validation) — 세포 데이터로 환자 수준 약물반응 예측

**자체 신약 파이프라인**
- 항암제: Proj.A~D (Target검증~Lead Opt 단계)
- 항생제: Proj.E (Hit/Lead → Activity평가 → Lead Opt)

---

## BIO USA 2026 참석 목적 (3연속 참가)

**핵심 목표**: PoC/파일럿 계약, 빅파마 파트너링 미팅, 글로벌 학술 네트워크

**1. Pilot Program** (최우선)
- 환자 코호트 + 후보 화합물 → ChemResponse로 patient-level response prediction 공동 실행
- 커밋 없음, 빠른 가치 증명

**2. Co-development Partner**
- Oncology 특화 proprietary translational dataset 보유 기업
- 특정 tumor type / indication 모델 파인튜닝 공동 개발

**3. Commercial Deployment / Strategic Investment**
- Private Runtime (고객 AWS VPC) 도입 논의
- 단순 FI보다 **제약사/화장품사의 SI(전략적투자)** 우선 — 2027 Series A 30~50억 목표

---

## 협력/세일즈 타깃 기준

**세일즈 타깃 (DrugVLAB 직접 사용)**
- Oncology pipeline 보유 바이오텍 / 제약사 (translational research 팀)
- Kinase inhibitor, PPI inhibitor 개발사
- Patient tumor RNA-seq 데이터 보유 / biomarker 전략 팀
- Phase I→II translation 실패 경험 있는 조직
- Drug toxicity / ADME 예측 필요 팀 (ChemTox 출시 예정)
- 데이터 보안 요건 강한 대형 제약사 / 병원

**파트너십 타깃 (협업 / BD / SI)**
- Translational CRO: ChemResponse 엔진 서비스 탑재
- Genomics / multi-omics 플랫폼: THERAPI 연동
- AI drug discovery 플랫폼: 모듈 라이선싱
- 글로벌 제약사: 자체 파이프라인 기술이전 파트너 (항암제 Proj.B/D/E)
- SI 투자 가능 제약사·화장품사 (현재 협의중)

**필터 아웃**
- Non-oncology 전용 파이프라인 (희귀질환, 감염병 등)
- Device / diagnostics only
- Pre-seed 단계 (구매력 없음)

---

## 파트너 탐색 도구

- **브라우저**: `tools/camofox-browser/` (Anti-detection, Node.js)
  - 실행: `cd tools/camofox-browser && yarn start` → `http://localhost:9377`
  - 포트 충돌 시 이미 실행 중인 것 — 별도로 재시작 불필요
  - **최초 실행 후 `npm rebuild better-sqlite3` 필요** (네이티브 바인딩 오류 발생 시)
- **인증**: `auth_data.json` (localStorage 포함 — 절대 커밋 금지)
- **탐색 URL**: `https://partner.bio.org/conference/86/search`
- **Python**: `/opt/homebrew/Caskroom/miniconda/base/bin/python`
- **스크래핑 코드**: `src/` 디렉토리에 저장 후 실행
- **작업 디렉토리**: 항상 `/Users/seokcholhong/workspace/biousa` — `/tmp` 등 임시 경로 사용 금지

### 인증 방식 (중요)

`partner.bio.org`는 **Microsoft MSAL.js** 기반 인증 → 토큰이 **localStorage**에 저장됨. `cookies.json`(EditThisCookie)만으로는 로그인 불가.

**auth_data.json 수집 방법** — Chrome에서 `partner.bio.org` 접속 후 F12 → Console:
```js
copy(JSON.stringify({
  cookies: document.cookie,
  localStorage: {...localStorage},
  sessionStorage: {...sessionStorage}
}))
```
결과를 `auth_data.json`으로 저장.

### 로그인 세션 주입 절차 (매번 필요)
./src/inject_session.py
```
1. better-sqlite3 확인: npm rebuild better-sqlite3 (첫 실행 또는 오류 시)

2. cookies.json 쿠키 주입
   POST /sessions/biousa-agent/cookies  {"cookies": [...변환된 쿠키...]}
   - sameSite 변환: no_restriction→None, lax→Lax, strict→Strict, unspecified→None

3. 탭 생성 (partner.bio.org로 직접 열면 즉시 로그인 redirect됨 — localStorage 주입 불가)
   대신: partner.bio.org로 탭 열자마자(1초 내) evaluate로 localStorage 주입 + window.location 이동
   POST /tabs  {"userId":"biousa-agent","sessionKey":"s1","url":"https://partner.bio.org/conference/86/search"}
   → tabId 받은 후 즉시(sleep 1):
   POST /tabs/{tabId}/evaluate  {"expression":"(function(){...localStorage.setItem...window.location.href='https://partner.bio.org/conference/86/search';})()","userId":"biousa-agent"}

4. 7초 대기 후 snapshot으로 확인 — URL이 partner.bio.org/conference/86/search이고 "30867 Results" 텍스트 보이면 성공
```

### camofox API 패턴

```
# 탭 생성
POST http://localhost:9377/tabs
{"userId":"biousa-agent","sessionKey":"main","url":"https://partner.bio.org/..."}

# 스냅샷 (snapshot 필드에 접근성 트리, html 필드는 비어있음)
GET http://localhost:9377/tabs/{tabId}/snapshot?userId=biousa-agent

# 클릭
POST http://localhost:9377/tabs/{tabId}/click
{"ref":"e15","userId":"biousa-agent"}

# 타이핑
POST http://localhost:9377/tabs/{tabId}/type
{"ref":"e15","text":"oncology","userId":"biousa-agent"}

# 키 입력
POST http://localhost:9377/tabs/{tabId}/press
{"ref":"e17","key":"Enter","userId":"biousa-agent"}

# 스크롤
POST http://localhost:9377/tabs/{tabId}/scroll
{"x":760,"y":600,"deltaY":3000,"userId":"biousa-agent"}

# 대기
POST http://localhost:9377/tabs/{tabId}/wait
{"timeout":2000,"userId":"biousa-agent"}

# evaluate (return문 금지 — IIFE 사용)
POST http://localhost:9377/tabs/{tabId}/evaluate
{"expression":"(function(){...})()","userId":"biousa-agent"}

# 스크린샷 확인
GET http://localhost:9377/tabs/{tabId}/screenshot?userId=biousa-agent
```

### API 엔드포인트 (참고)

```
https://api.partner.bio.org/prod-search   ← 검색
https://api.partner.bio.org/prod-company  ← 회사 정보
https://api.partner.bio.org/prod-conference
https://api.partner.bio.org/prod-corebackend
```
단, 이 API는 직접 호출 시 404/406 반환 — 정확한 경로 미파악. **브라우저 스크래핑 방식 사용**.

### 스크래핑 snapshot 파싱 요령

`snapshot` 필드가 접근성 트리 텍스트. `html` 필드는 항상 비어있음.
회사 카드 패턴:
```
button "COMPANY NAME Request ... TYPE COUNTRY OWNERSHIP":
  heading "COMPANY NAME"
  link "Website": /url: https://...
  text: ... TYPE COUNTRY
  paragraph: OWNERSHIP
button "DESCRIPTION"
```

### 결과 저장
- `data/bio_companies_raw.json` — 원본 스크래핑 결과
- `data/bio_companies_filtered.json` — 협력 후보 필터링 결과
- `biousa/representatives/*.md` — 최종 선정 기업별 상세 분석