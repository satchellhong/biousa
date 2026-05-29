# 개발 세션 로그

## 진행 요약

Partner Central(AWS 파트너 포털) 로그인 세션을 camofox-browser를 통해 자동화하고,
FTR 관련 문서를 수집한 뒤 MCP 서버 뼈대를 구성했습니다.

---

## 1단계: camofox-browser 실행

`tools/camofox-browser/` 디렉토리에 이미 camofox 소스가 존재했음.

```bash
cd tools/camofox-browser
yarn start
# → http://localhost:9377 에서 REST API 서버 구동
```

실행 로그에서 확인된 사항:
- `camoufox launched` — Firefox 기반 anti-detection 브라우저 정상 기동
- `persistence plugin enabled` — 세션이 `~/.camofox/profiles/`에 자동 저장됨
- VNC는 비활성 상태 (`ENABLE_VNC=1` 환경변수로 활성화 가능)

---

## 2단계: Partner Central 쿠키 주입

AWS Partner Central은 Salesforce 기반 SSO라 JWT 직접 주입이 안됨.
Chrome에서 로그인 후 쿠키를 export해서 camofox에 주입하는 방식 사용.

### 쿠키 export 방법
1. Chrome에서 `partnercentral.awspartner.com` 로그인
2. Chrome 확장 **EditThisCookie** 설치
3. Partner Central 탭에서 확장 열기 → Export(JSON 형식) → 복사
4. `cookies.json` 파일로 저장

### Chrome export 포맷 → Playwright 포맷 변환 필요

Chrome export 포맷:
```json
[{
  "domain": "partnercentral.awspartner.com",
  "hostOnly": true,
  "sameSite": "no_restriction",
  ...
}]
```

camofox(Playwright)가 요구하는 포맷:
```json
[{
  "domain": "partnercentral.awspartner.com",
  "sameSite": "None",   ← no_restriction → None 변환 필요
  ...
}]
```

변환 포인트:
- `sameSite` 값 매핑: `no_restriction→None`, `lax→Lax`, `strict→Strict`
- `hostOnly: true` 이면 domain에 `.` 접두사 붙이지 않음

### 쿠키 주입 API 호출

```bash
curl -X POST http://localhost:9377/sessions/ftr-agent/cookies \
  -H 'Content-Type: application/json' \
  -d '{"cookies": [변환된_쿠키_배열]}'
# → {"ok":true,"userId":"ftr-agent","count":21}
```

변환 + 주입 코드: `src/tools/browser.py` → `inject_cookies()`

---

## 3단계: Partner Central 페이지 접근

탭 열기 시 `userId`와 `sessionKey` 둘 다 필수임 (sessionKey 없으면 에러).

```bash
# 탭 열기
curl -X POST http://localhost:9377/tabs \
  -H 'Content-Type: application/json' \
  -d '{"userId":"ftr-agent","sessionKey":"main","url":"https://partnercentral.awspartner.com"}'
# → {"tabId":"8ee88ed1-...","url":"https://partnercentral.awspartner.com/partnercentral2/s/"}

# 스냅샷 조회 (userId 쿼리 파라미터 필수)
curl "http://localhost:9377/tabs/{tabId}/snapshot?userId=ftr-agent"
```

스냅샷으로 로그인 확인:
```
- paragraph: Welcome, seokchol hong
- paragraph: AIGENDRUG Co., Ltd.
```

---

## 4단계: FTR 리소스 페이지 접근 및 파일 다운로드

```bash
# FTR 가이드 리소스 페이지로 이동
curl -X POST http://localhost:9377/tabs/{tabId}/navigate \
  -H 'Content-Type: application/json' \
  -d '{"userId":"ftr-agent","url":"https://partnercentral.awspartner.com/partnercentral2/s/resources?Id=0690h00000BGRJhAAP"}'

# 스냅샷에서 Download 버튼 ref 확인 → e39
# Download 버튼 클릭
curl -X POST http://localhost:9377/tabs/{tabId}/click \
  -H 'Content-Type: application/json' \
  -d '{"userId":"ftr-agent","ref":"e39"}'

# 다운로드 목록 확인 (includeData=true로 base64 데이터 포함)
curl "http://localhost:9377/tabs/{tabId}/downloads?userId=ftr-agent&includeData=true"
```

다운로드 저장 코드: `src/tools/browser.py` → `save_download()`

---

## 5단계: 수집된 문서

| 파일 | 출처 | 설명 |
|---|---|---|
| `docs/AWS_FTR_Guide_latest.pdf` | Partner Central (로그인 필요) | FTR 가이드 최신판 (Jan 2026) |
| `docs/FTR_Self_Assessment.xlsx` | S3 공개 버킷 | Self-Assessment 엑셀 |
| `docs/FTR_Checklist_KO.html` | S3 공개 버킷 | 한국어 체크리스트 |

공개 S3 체크리스트 URL:
```
https://apn-checklists.s3.amazonaws.com/foundational/partner-hosted/partner-hosted/CVLHEC5X7.html
https://apn-checklists.s3.amazonaws.com/foundational/partner-hosted/partner-hosted/ko/CVLHEC5X7.html
https://apn-checklists.s3.amazonaws.com/foundational/partner-hosted/partner-hosted/CVLHEC5X7/Partner%20Hosted%20Foundational%20Technical%20Review%20Self-Assessment.xlsx
```

---

## 6단계: MCP 서버 구조

```
src/
├── server.py          # FastMCP 서버 진입점 (stdio transport)
├── tools/
│   ├── browser.py     # camofox REST API 래퍼
│   ├── checklist.py   # S3 체크리스트 파싱 및 캐싱
│   └── progress.py    # 항목별 상태/증거 관리
└── data/
    └── checklist.json # 파싱된 체크리스트 캐시 (자동 생성)
```

### MCP 툴 목록

| 툴 | 설명 |
|---|---|
| `ftr_get_checklist` | 카테고리별 FTR 항목 조회 |
| `ftr_get_summary` | 전체 진행 현황 요약 |
| `ftr_update_status` | 항목 상태/증거 업데이트 |
| `ftr_get_pending` | 미완료 항목 목록 |
| `ftr_get_roadmap` | 카테고리별 완료율 로드맵 |
| `browser_inject_cookies` | 쿠키 파일 → camofox 주입 |
| `browser_open_tab` | 탭 열기 |
| `browser_navigate` | 탭 이동 |
| `browser_snapshot` | 페이지 스냅샷 |
| `browser_click` | 요소 클릭 |
| `browser_save_download` | 다운로드 파일 저장 |

---

## 다음 단계

- [ ] `src/data/checklist.json` 초기화 (`ftr_get_checklist()` 호출로 자동 생성)
- [ ] Claude Code 설정에 MCP 서버 등록 (`~/.claude/settings.json`)
- [ ] Partner Hosted FTR Calibration Guide PDF 다운로드 (Partner Central 리소스 페이지)
- [ ] CIS Benchmark 리포트 생성 (AWS Security Hub)
- [ ] Architecture Diagram 준비

---

## 참고: camofox API 주요 엔드포인트

| Method | Endpoint | 설명 |
|---|---|---|
| POST | `/sessions/:userId/cookies` | 쿠키 주입 |
| POST | `/tabs` | 탭 생성 (userId + sessionKey 필수) |
| POST | `/tabs/:id/navigate` | URL 이동 |
| GET | `/tabs/:id/snapshot?userId=` | 접근성 트리 스냅샷 |
| POST | `/tabs/:id/click` | 요소 클릭 |
| POST | `/tabs/:id/type` | 텍스트 입력 |
| POST | `/tabs/:id/scroll` | 스크롤 |
| GET | `/tabs/:id/downloads?userId=&includeData=true` | 다운로드 파일 (base64) |
