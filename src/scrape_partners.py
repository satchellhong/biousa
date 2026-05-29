#!/usr/bin/env /opt/homebrew/Caskroom/miniconda/base/bin/python
"""
BIO USA 2026 partner.bio.org 스크래핑
- CSV append 방식으로 즉시 저장
- 타깃: 우리 플랫폼 구매/협력 가능 기업만 (비용 지불 공급사 제외)
"""

import csv
import json
import os
import re
import time
import urllib.request
import urllib.parse

BASE = "http://localhost:9377"
USER = "biousa-agent"
WORK_DIR = "/Users/seokcholhong/workspace/biousa"
CSV_PATH = WORK_DIR + "/data/bio_companies_raw.csv"
FILTERED_CSV_PATH = WORK_DIR + "/data/bio_companies_filtered.csv"

CSV_FIELDS = ["name", "country", "company_type", "ownership", "website", "description", "search_keyword", "relevant", "relevance_score"]

SEARCH_KEYWORDS = [
    "oncology",
    "kinase",
    "AI drug discovery",
    "translational",
    "RNA-seq",
    "drug response",
    "ADME",
    "biomarker",
    "computational chemistry",
    "drug toxicity",
    "machine learning drug",
    "patient stratification",
]

# 우리 고객/파트너가 될 수 있는 회사 키워드
INCLUDE_KEYWORDS = [
    "oncol", "cancer", "tumor", "kinase", "ppi ", "protein-protein",
    "translational", "rna-seq", "rnaseq", "biomarker", "drug response",
    "drug discovery", "ai drug", "adme", "toxicolog", "chemoinformat",
    "computational", "in silico", "machine learning", "deep learning",
    "therapeutic r&d", "phase i", "phase ii", "clinical stage",
    "lead optim", "hit-to-lead", "medicinal chem", "patient stratif",
    "multi-omics", "genomics", "precision medicine",
]

# 우리가 돈을 써야 하는 공급사 — 필터 아웃
SUPPLIER_KEYWORDS = [
    "cro only", "cmo only", "contract research only",
    "staffing", "recruitment", "headhunting",
    "legal service", "patent service", "ip service",
    "accounting", "consulting only",
    "animal health", "veterinar", "agricultural", "dental", "ophthalmol",
    "device only", "diagnostics only", "medical device only",
]

# 회사 타입 중 공급사에 해당하는 것 (설명에 없어도 타입으로 판단)
SUPPLIER_TYPES = [
    "staffing", "legal", "accounting", "financial service",
    "real estate", "insurance",
]


def api(method, path, body=None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def get_snapshot(tab_id):
    req = urllib.request.Request(BASE + f"/tabs/{tab_id}/snapshot?userId={USER}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def navigate(tab_id, url):
    return api("POST", f"/tabs/{tab_id}/navigate", {"url": url, "userId": USER})


def click(tab_id, ref):
    return api("POST", f"/tabs/{tab_id}/click", {"ref": ref, "userId": USER})


def evaluate(tab_id, expr):
    return api("POST", f"/tabs/{tab_id}/evaluate", {"expression": expr, "userId": USER})


def inject_session():
    with open(WORK_DIR + "/cookies.json") as f:
        cookies = json.load(f)
    for c in cookies:
        ss = c.get("sameSite", "")
        if ss in ("no_restriction", "unspecified", ""):
            c["sameSite"] = "None"
        elif ss == "lax":
            c["sameSite"] = "Lax"
        elif ss == "strict":
            c["sameSite"] = "Strict"
    api("POST", "/sessions/biousa-agent/cookies", {"cookies": cookies})

    tab = api("POST", "/tabs", {"userId": USER, "sessionKey": "scrape_main", "url": "https://partner.bio.org/conference/86/search"})
    tab_id = tab["tabId"]

    with open(WORK_DIR + "/auth_data.json") as f:
        auth = json.load(f)
    ls = auth["localStorage"]
    lines = ["localStorage.setItem({},{});".format(json.dumps(k), json.dumps(v)) for k, v in ls.items()]
    script = "(function(){" + "".join(lines) + "window.location.href='https://partner.bio.org/conference/86/search';})()"
    time.sleep(1)
    api("POST", f"/tabs/{tab_id}/evaluate", {"expression": script, "userId": USER})
    time.sleep(8)

    with open(WORK_DIR + "/src/active_tab.txt", "w") as f:
        f.write(tab_id)
    print(f"  세션 재주입 완료: {tab_id}")
    return tab_id


def get_active_tab():
    try:
        with open(WORK_DIR + "/src/active_tab.txt") as f:
            tab_id = f.read().strip()
        get_snapshot(tab_id)
        return tab_id
    except Exception:
        return None


def load_existing_names():
    """기존 CSV에서 이름 + 완료 키워드 로드"""
    seen = set()
    done_keywords = set()
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                seen.add(row["name"])
                done_keywords.add(row["search_keyword"])
    return seen, done_keywords


def append_to_csv(companies):
    """CSV에 행 추가 (파일 없으면 헤더 포함 생성)"""
    os.makedirs(WORK_DIR + "/data", exist_ok=True)
    file_exists = os.path.exists(CSV_PATH)
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        writer.writerows(companies)


def parse_companies(snap_text):
    companies = []
    heading_pattern = re.compile(r'heading "([^"]+)" \[level=2\]')
    website_pattern = re.compile(r'/url: (https?://[^\s\n]+)')
    lines = snap_text.split('\n')

    i = 0
    while i < len(lines):
        m = heading_pattern.search(lines[i])
        if m:
            name = m.group(1)
            block = '\n'.join(lines[max(0, i-5):i+25])

            wm = website_pattern.search(block)
            website = wm.group(1) if wm else ""

            text_match = re.search(r'text: (?:Updated [\w ]+ ago )?(.*?)(?:\n\s*paragraph:|\n\s*-\s*button|\Z)', block)
            type_country_raw = text_match.group(1).strip() if text_match else ""
            type_country_raw = re.sub(r'^Updated \S+ ', '', type_country_raw).strip()

            # 마지막 단어를 국가로 추출 시도 (영어 단어들)
            parts = type_country_raw.rsplit(' ', 1)
            country = parts[-1] if len(parts) > 1 and parts[-1][0].isupper() else ""
            company_type = type_country_raw

            own_match = re.search(r'paragraph: (Public|Private|Academic|Government|Non-?profit)', block)
            ownership = own_match.group(1) if own_match else ""

            desc = ""
            for j in range(i+1, min(i+35, len(lines))):
                if 'heading "' in lines[j] and '[level=2]' in lines[j]:
                    break
                line = lines[j].strip()
                if line.startswith('- button "') and len(line) > 80:
                    btn_text = re.sub(r'^- button "', '', line).rstrip('"')
                    skip = ['Request', 'Prior Meetings', 'Notes', 'Website', 'Updated', 'View']
                    if not any(x in btn_text for x in skip) and len(btn_text) > 50:
                        desc = btn_text[:500]
                        break

            companies.append({
                "name": name,
                "country": country,
                "company_type": company_type,
                "website": website,
                "ownership": ownership,
                "description": desc,
            })
        i += 1

    return companies


def find_next_page_ref(snap_text):
    for line in snap_text.split('\n'):
        if 'go to next page' in line.lower():
            m = re.search(r'\[(\w+)\]', line)
            if m:
                return m.group(1)
    return None


def get_page_info(snap_text):
    cur_m = re.search(r'combobox "(\d+)"', snap_text)
    tot_m = re.search(r'paragraph: of (\d+)', snap_text)
    if cur_m and tot_m:
        return int(cur_m.group(1)), int(tot_m.group(1))
    return 1, 1


def is_relevant(company):
    """
    우리와 거래 가능한 회사인지 판단:
    - 포함: 우리 플랫폼 구매/협력 가능 (바이오텍, 파마, AI 플랫폼 등)
    - 제외: 우리가 돈을 써야 하는 순수 공급사 (서비스 판매자)
    """
    text = (
        company.get("name","") + " " +
        company.get("description","") + " " +
        company.get("company_type","")
    ).lower()

    # 순수 공급사 제외
    if any(kw in text for kw in SUPPLIER_KEYWORDS):
        return False, 0
    if any(kw in company.get("company_type","").lower() for kw in SUPPLIER_TYPES):
        return False, 0

    score = sum(1 for kw in INCLUDE_KEYWORDS if kw in text)
    return score >= 1, score


def search_and_scrape(tab_id, keyword, seen_names, max_pages=200):
    print(f"\n[{keyword}] 검색 시작")

    search_url = "https://partner.bio.org/conference/86/search?keyword={}&sortBy=relevancy".format(
        urllib.parse.quote(keyword)
    )
    navigate(tab_id, search_url)
    time.sleep(4)

    snap = get_snapshot(tab_id)
    snap_text = snap.get("snapshot", "")
    for line in snap_text.split('\n'):
        if 'Companies' in line and 'button' in line and re.search(r'\d{2,}', line):
            m = re.search(r'\[(\w+)\]', line)
            if m:
                click(tab_id, m.group(1))
                time.sleep(3)
                break

    keyword_new_count = 0
    page = 1

    while page <= max_pages:
        snap3 = get_snapshot(tab_id)
        page_text = snap3.get("snapshot", "")

        cur_page, total_pages = get_page_info(page_text)
        if page == 1:
            count_m = re.search(r'(\d+) Results', page_text)
            total_results = count_m.group(1) if count_m else "?"
            print(f"  총 {total_results}개 결과, {total_pages}페이지")

        companies = parse_companies(page_text)
        page_new = []
        for c in companies:
            if c["name"] not in seen_names:
                seen_names.add(c["name"])
                c["search_keyword"] = keyword
                rel, score = is_relevant(c)
                c["relevant"] = rel
                c["relevance_score"] = score
                page_new.append(c)
                keyword_new_count += 1

        # 페이지마다 즉시 CSV append
        if page_new:
            append_to_csv(page_new)

        print(f"  페이지 {cur_page}/{total_pages}: +{len(page_new)}개 저장 (키워드 누적 {keyword_new_count}개)")

        if cur_page >= total_pages or cur_page >= max_pages:
            print(f"  마지막 페이지 도달")
            break

        next_ref = find_next_page_ref(page_text)
        if not next_ref:
            result = evaluate(tab_id, """(function(){
                var btns = document.querySelectorAll('button[aria-label*="next"], button[aria-label*="Next"]');
                if(btns.length > 0){ btns[btns.length-1].click(); return 'clicked'; }
                return 'not found';
            })()""")
            if result.get("result") != "clicked":
                print(f"  다음 페이지 버튼 못 찾음, 종료")
                break
        else:
            click(tab_id, next_ref)

        page += 1
        time.sleep(3)

    return keyword_new_count


def save_filtered():
    """raw CSV에서 필터링된 CSV 생성"""
    filtered = []
    if not os.path.exists(CSV_PATH):
        return
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("relevant") == "True":
                filtered.append(row)

    filtered.sort(key=lambda x: int(x.get("relevance_score","0") or 0), reverse=True)

    with open(FILTERED_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(filtered)

    return filtered


def main():
    print("=== BIO USA 2026 파트너 스크래핑 ===")

    tab_id = get_active_tab()
    if not tab_id:
        print("탭 없음 — 세션 재주입 중...")
        tab_id = inject_session()
    print(f"탭: {tab_id}")

    seen_names, done_keywords = load_existing_names()
    print(f"기존 수집: {len(seen_names)}개사, 완료 키워드: {done_keywords}")

    for keyword in SEARCH_KEYWORDS:
        if keyword in done_keywords:
            print(f"\n[{keyword}] 이미 완료, 스킵")
            continue

        try:
            get_snapshot(tab_id)
        except Exception:
            print(f"  탭 만료 — 세션 재주입 중...")
            tab_id = inject_session()

        count = search_and_scrape(tab_id, keyword, seen_names)
        print(f"  → [{keyword}] 완료: {count}개 추가")

    # 최종 통계
    seen_final, _ = load_existing_names()
    print(f"\n=== 총 수집: {len(seen_final)}개 ===")

    filtered = save_filtered()
    print(f"필터링: {len(filtered)}개 → {FILTERED_CSV_PATH}")

    print("\n=== 상위 타깃 기업 (relevance 순) ===")
    for i, c in enumerate(filtered[:30], 1):
        score = c.get("relevance_score","0")
        print(f"{i:2}. [{score}점] {c['name']} ({c.get('country','')})")
        if c.get("description"):
            print(f"    {c['description'][:120]}")


if __name__ == "__main__":
    main()
