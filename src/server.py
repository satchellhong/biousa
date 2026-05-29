"""
AWS FTR MCP 서버.

실행:
    conda activate aws_ftr
    python src/server.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from mcp.server.fastmcp import FastMCP
from src.tools.checklist import load_checklist, get_by_category, get_summary
from src.tools.progress import update_status, get_pending, get_roadmap
from src.tools.browser import inject_cookies, open_tab, navigate, snapshot, click, save_download
from src.tools.iac_validator import validate_iac
from src.tools.report_generator import generate_report, generate_full_report
from src.tools.console_checker import check_console

mcp = FastMCP("AWS FTR Assistant")


# ── 체크리스트 조회 ──────────────────────────────────────────────────────────

@mcp.tool()
def ftr_get_checklist(category: str = "") -> dict:
    """
    FTR 체크리스트 항목 조회.
    category를 지정하면 해당 카테고리만 반환 (예: IAM, S3, Network).
    비워두면 전체 반환.
    """
    if category:
        return {"controls": get_by_category(category)}
    data = load_checklist()
    return data


@mcp.tool()
def ftr_get_summary() -> dict:
    """전체 FTR 진행 현황 요약 (총 항목 수, 완료/진행중/미완료 수, 진행률)."""
    return get_summary()


# ── 진행 상태 관리 ───────────────────────────────────────────────────────────

@mcp.tool()
def ftr_update_status(control_id: str, status: str, evidence: str = "") -> dict:
    """
    FTR 항목 상태 업데이트.

    control_id: requirement_ARC-001 형식 (ftr_get_checklist로 확인)
    status: 미완료 | 진행중 | 완료 | 해당없음
    evidence: 증거 링크 또는 메모 (선택)
    """
    return update_status(control_id, status, evidence)


@mcp.tool()
def ftr_get_pending() -> list:
    """아직 완료되지 않은 FTR 항목 목록 반환."""
    return get_pending()


@mcp.tool()
def ftr_get_roadmap() -> list:
    """카테고리별 완료율 기반 진행 로드맵. 미완료 비율 높은 순으로 정렬."""
    return get_roadmap()


# ── IaC 검증 ────────────────────────────────────────────────────────────────

@mcp.tool()
def ftr_validate_iac(iac_dir: str = "") -> dict:
    """
    iac/ 폴더 Terraform 코드를 읽기 전용으로 파싱해 FTR 항목별 PASS/FAIL/MANUAL 반환.

    iac_dir: .tf 파일이 있는 디렉터리 경로 (비워두면 기본 경로 사용)
    반환: summary(pass/fail/manual 수), fail_items(즉시 수정 필요), manual_items(수동 확인 필요)

    주의: 이 툴은 코드를 읽기만 합니다. terraform 명령을 실행하지 않습니다.
    """
    return validate_iac(iac_dir if iac_dir else None)


@mcp.tool()
def ftr_generate_report(iac_dir: str = "", save: bool = True) -> str:
    """
    IaC 검증 후 마크다운 리포트를 생성하여 반환.

    iac_dir: .tf 파일 디렉터리 (비워두면 기본 경로)
    save: True이면 docs/IaC_검증_리포트_<날짜>.md 로 저장
    반환: 마크다운 리포트 문자열
    """
    import datetime
    validation = validate_iac(iac_dir if iac_dir else None)
    if "error" in validation:
        return f"오류: {validation['error']}"

    output_path = None
    if save:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        output_path = f"docs/IaC_검증_리포트_{today}.md"

    return generate_report(validation, output_path)


@mcp.tool()
def ftr_validate_and_update(iac_dir: str = "") -> dict:
    """
    IaC 검증 후 PASS 항목의 progress 상태를 자동으로 '완료'로 업데이트.

    iac_dir: .tf 파일 디렉터리 (비워두면 기본 경로)
    반환: 검증 결과 + 업데이트된 항목 목록
    """
    validation = validate_iac(iac_dir if iac_dir else None)
    if "error" in validation:
        return validation

    updated = []
    for item in validation.get("results", []):
        if item["status"] == "PASS":
            evidence = "; ".join(item.get("evidence", []))
            result = update_status(item["id"], "완료", f"IaC 자동 검증: {evidence}")
            if result.get("ok"):
                updated.append(item["id"])

    validation["auto_updated"] = updated
    validation["auto_updated_count"] = len(updated)
    return validation


# ── boto3 콘솔 자동 점검 ─────────────────────────────────────────────────────

@mcp.tool()
def ftr_check_console(checks: str = "") -> dict:
    """
    boto3로 AWS 계정을 읽기 전용으로 점검하여 FTR 항목별 PASS/FAIL 반환.

    점검 항목: 루트 MFA, 루트 액세스 키, 계정 연락처, IAM 사용자 MFA,
               자격증명 교체, 비밀번호 정책, 기본 VPC SG, CloudTrail,
               Security Hub CIS, Business Support

    checks: 특정 항목만 점검 (쉼표 구분, 예: "requirement_ARC-004,requirement_IAM-001")
            비워두면 전체 점검.
    반환: summary(pass/fail/warn/manual), results (각 항목별 상태 + 근거)

    주의: 이 툴은 읽기 전용입니다. 리소스를 생성/수정/삭제하지 않습니다.
    """
    check_list = [c.strip() for c in checks.split(",") if c.strip()] if checks else None
    return check_console(check_list)


@mcp.tool()
def ftr_full_report(iac_dir: str = "", save: bool = True) -> str:
    """
    IaC 검증 + boto3 콘솔 점검을 합쳐 통합 마크다운 리포트 반환.

    IaC MANUAL 항목 중 콘솔 점검으로 판정 가능한 것은 실제 결과(PASS/FAIL)로 교체됨.
    같은 항목 ID가 두 곳에 있으면 더 나쁜 상태(FAIL > WARN > MANUAL > PASS)를 사용.

    iac_dir: .tf 파일 디렉터리 (비워두면 기본 경로)
    save: True이면 docs/FTR_통합_리포트_<날짜>.md 로 저장
    반환: 통합 마크다운 리포트 문자열
    """
    import datetime
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    iac = validate_iac(iac_dir if iac_dir else None)
    console = check_console()
    output_path = f"docs/FTR_통합_리포트_{today}.md" if save else None
    return generate_full_report(iac, console, output_path)


# ── Partner Central 브라우저 접근 ────────────────────────────────────────────

@mcp.tool()
def browser_inject_cookies(cookies_json_path: str) -> dict:
    """
    쿠키 파일을 camofox에 주입해 Partner Central 인증 세션 생성.

    cookies_json_path: Chrome 확장(EditThisCookie)으로 export한 JSON 파일 경로
    camofox 서버가 localhost:9377에서 실행 중이어야 함.
    """
    return inject_cookies(cookies_json_path)


@mcp.tool()
def browser_open_tab(url: str) -> str:
    """camofox에서 새 탭 열기. tabId 반환."""
    return open_tab(url)


@mcp.tool()
def browser_navigate(tab_id: str, url: str) -> dict:
    """탭을 새 URL로 이동."""
    return navigate(tab_id, url)


@mcp.tool()
def browser_snapshot(tab_id: str) -> str:
    """페이지 접근성 트리 스냅샷 반환. 링크/버튼의 ref(e1, e2...) 확인에 사용."""
    return snapshot(tab_id)


@mcp.tool()
def browser_click(tab_id: str, ref: str) -> dict:
    """스냅샷에서 확인한 ref로 요소 클릭 (예: e39)."""
    return click(tab_id, ref)


@mcp.tool()
def browser_save_download(tab_id: str, save_path: str) -> str:
    """탭에서 캡처된 다운로드 파일을 지정 경로에 저장."""
    return save_download(tab_id, save_path)


if __name__ == "__main__":
    mcp.run(transport="stdio")
