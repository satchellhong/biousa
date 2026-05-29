# DrugVLAB — 사용자 스토리

## 역할 정의

| Role | 정의 | Cognito attribute |
|---|---|---|
| `researcher` | 워크플로우 실행, 본인 결과 확인, review 요청 | `custom:role = researcher` |
| `reviewer` | 그룹 내 결과 열람, go/hold/no-go 판정, 메모 작성 | `custom:role = reviewer` |
| `admin` | 기존 권한 + 역할 부여/회수, 전체 history 열람 | `custom:is_admin = true` |

기존 `is_admin` 로직은 그대로 유지. role은 별도 attribute로 관리.

---

## 사용자 스토리

### Researcher

**US-01** — 워크플로우 실행 후 결과 확인
> researcher로서, 실행이 완료된 라이브러리 결과 화면에서 Recommendation Card와 Evidence Panel을 확인하고 싶다. 그래야 reviewer에게 검토를 요청할 때 어떤 근거가 있는지 직접 먼저 파악할 수 있다.

**US-02** — 검토 요청
> researcher로서, 결과 화면에서 "Request Review" 버튼을 눌러 그룹 내 reviewer에게 검토를 요청할 수 있어야 한다. reviewer는 Pending Reviews 목록에서 이를 확인한다.

**US-03** — review 이력 확인
> researcher로서, 내가 실행한 라이브러리에 대해 reviewer가 남긴 decision과 메모를 결과 화면에서 확인할 수 있어야 한다.

---

### Reviewer

**US-04** — Pending Review 목록 확인
> reviewer로서, 내가 속한 그룹 내에서 검토 요청이 들어온 라이브러리 목록을 한 화면에서 볼 수 있어야 한다. 워크플로우 종류, 요청자, 요청 시각이 보여야 한다.

**US-05** — 결과 검토 및 판정
> reviewer로서, 결과 상세 화면에서 Recommendation Card, Evidence Panel, Context Panel을 보고 go / hold / no-go 중 하나를 선택한 뒤 메모와 다음 실험 제안을 남길 수 있어야 한다.

**US-06** — Decision Card export 요청
> reviewer로서, review를 완료한 후 "Export Decision Card" 버튼을 눌러 해당 결과의 구조화된 요약(JSON 또는 PDF)을 내려받을 수 있어야 한다. 이 카드는 회의 자료로 바로 사용할 수 있어야 한다.

**US-07** — Decision History 조회
> reviewer로서, 그룹 내 전체 decision history를 날짜·워크플로우·판정 결과 기준으로 필터링해서 볼 수 있어야 한다.

---

### Admin

**US-08** — 역할 부여/회수
> admin으로서, Admin 페이지에서 특정 사용자에게 reviewer 역할을 부여하거나 회수할 수 있어야 한다. 변경은 즉시 반영되어야 한다.

**US-09** — 전체 decision history 열람
> admin으로서, 조직 전체의 decision history를 조회하고 필요 시 export할 수 있어야 한다. (audit 목적)

---

## 승인 워크플로우 (상세)

```
[Researcher]
    1. 워크플로우 실행 → COMPLETED
    2. 결과 확인 (Recommendation Card + Evidence Panel)
    3. "Request Review" 클릭
       → Reviewer의 Pending Reviews에 항목 추가
       → (옵션) 이메일/알림 발송

[Reviewer]
    4. Pending Reviews에서 항목 선택
    5. 결과 상세 화면 열람
       → Recommendation Card
       → Evidence Panel (MoA, pathway, docking)
       → Context Panel (alignment, heterogeneity) — Clinical만
    6. Review Panel에서 판정 선택
       → GO / HOLD / NO-GO
       → Memo 작성
       → Suggested next experiment 작성
    7. "Submit Review" 클릭
       → Decision record DynamoDB 저장
       → Researcher에게 결과 통보
       → Decision Card 생성 가능 상태로 전환

[Researcher / Reviewer]
    8. "Export Decision Card" 클릭
       → JSON 즉시 다운로드 (v1)
       → PDF 생성 (v2)
```

---

## 엣지 케이스

| 상황 | 처리 |
|---|---|
| reviewer가 없는 그룹 | Request Review 버튼 비활성화, 안내 문구 표시 |
| 동일 라이브러리에 복수 review | 최신 review를 "current decision"으로 표시, 이전 review는 history에 누적 |
| re-run 후 기존 review | 이전 review는 archive 처리. 새 결과는 review pending 상태로 초기화 |
| reviewer가 본인 결과를 review | 허용 (자기 검토), admin이 별도 정책으로 제한 가능 |
