#!/usr/bin/env /opt/homebrew/Caskroom/miniconda/base/bin/python
"""
BIO USA 2026 partner.bio.org 스크래핑
- 페이지네이션: "go to next page" 버튼 클릭 (25개/페이지)
- 페이지마다 즉시 저장 (크래시 복구 가능)
- 탭 404 시 자동 세션 재주입
"""

import json
import os
import re
import time
import urllib.request
import urllib.parse

BASE = "http://localhost:9377"
USER = "biousa-agent"
WORK_DIR = "/Users/seokcholhong/workspace/biousa"
RAW_PATH = WORK_DIR + "/data/bio_companies_raw.json"
FILTERED_PATH = WORK_DIR + "/data/bio_companies_filtered.json"

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

INCLUDE_KEYWORDS = [
    "oncol", "cancer", "tumor", "kinase", "ppi ", "protein-protein",
    "translational", "rna-seq", "rnaseq", "biomarker", "drug response",
    "drug discovery", "ai drug", "adme", "toxicolog", "chemoinformat",
    "computational", "in silico", "machine learning", "deep learning",
    "therapeutic r&d", "phase i", "phase ii",
    "lead optim", "hit-to-lead", "medicinal chem", "patient stratif",
]

EXCLUDE_KEYWORDS = [
    "animal health", "veterinar", "agricultural", "dental", "ophthalmol",
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
    """쿠키 + localStorage 주입하여 새 탭 생성, tab_id 반환"""
    # 쿠키 주입
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

    # 탭 생성
    tab = api("POST", "/tabs", {"userId": USER, "sessionKey": "scrape_main", "url": "https://partner.bio.org/conference/86/search"})
    tab_id = tab["tabId"]

    # localStorage 주입
    with open(WORK_DIR + "/auth_data.json") as f:
        auth = json.load(f)
    ls = auth["localStorage"]
    lines = ["localStorage.setItem({},{});".format(json.dumps(k), json.dumps(v)) for k, v in ls.items()]
    script = "(function(){" + "".join(lines) + "window.location.href='https://partner.bio.org/conference/86/search';})()"
    time.sleep(1)
    api("POST", f"/tabs/{tab_id}/evaluate", {"expression": script, "userId": USER})
    time.sleep(8)

    # 저장
    with open(WORK_DIR + "/src/active_tab.txt", "w") as f:
        f.write(tab_id)
    print(f"  세션 재주입 완료: {tab_id}")
    return tab_id


def get_active_tab():
    try:
        with open(WORK_DIR + "/src/active_tab.txt") as f:
            tab_id = f.read().strip()
        # 탭 살아있는지 확인
        get_snapshot(tab_id)
        return tab_id
    except Exception:
        pass
    return None


def load_existing():
    if os.path.exists(RAW_PATH):
        with open(RAW_PATH) as f:
            data = json.load(f)
        return data, {c["name"] for c in data}
    return [], set()


def save_raw(companies):
    os.makedirs(WORK_DIR + "/data", exist_ok=True)
    with open(RAW_PATH, "w", encoding="utf-8") as f:
        json.dump(companies, f, ensure_ascii=False, indent=2)


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
            type_country = text_match.group(1).strip() if text_match else ""
            type_country = re.sub(r'^Updated \S+ ', '', type_country).strip()

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
                        desc = btn_text[:400]
                        break

            companies.append({
                "name": name,
                "type_country": type_country,
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
    text = (company.get("name","") + " " + company.get("description","") + " " + company.get("type_country","")).lower()
    if any(kw in text for kw in EXCLUDE_KEYWORDS):
        return False, 0
    score = sum(1 for kw in INCLUDE_KEYWORDS if kw in text)
    return score >= 1, score


def search_and_scrape(tab_id, keyword, seen_names, all_companies, max_pages=200):
    """페이지네이션 방식으로 순회하며 수집, 페이지마다 즉시 저장"""
    print(f"\n[{keyword}] 검색 시작")

    search_url = "https://partner.bio.org/conference/86/search?keyword={}&sortBy=relevancy".format(
        urllib.parse.quote(keyword)
    )
    navigate(tab_id, search_url)
    time.sleep(4)

    # Companies 탭 클릭
    snap = get_snapshot(tab_id)
    snap_text = snap.get("snapshot", "")
    for line in snap_text.split('\n'):
        if 'Companies' in line and 'button' in line and re.search(r'\d{2,}', line):
            m = re.search(r'\[(\w+)\]', line)
            if m:
                click(tab_id, m.group(1))
                time.sleep(3)
                break

    new_companies = []
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
        added = 0
        for c in companies:
            if c["name"] not in seen_names:
                seen_names.add(c["name"])
                c["search_keyword"] = keyword
                rel, score = is_relevant(c)
                c["relevant"] = rel
                c["relevance_score"] = score
                new_companies.append(c)
                added += 1

        print(f"  페이지 {cur_page}/{total_pages}: +{added}개 (키워드 누적 {len(new_companies)}개)")

        # 페이지마다 즉시 저장
        if added > 0:
            save_raw(all_companies + new_companies)

        # 마지막 페이지 도달
        if cur_page >= total_pages or cur_page >= max_pages:
            print(f"  마지막 페이지 도달")
            break

        # 다음 페이지 버튼 클릭
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

    return new_companies


def filter_companies(companies):
    filtered = [c for c in companies if c.get("relevant", False)]
    filtered.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    return filtered


def main():
    print("=== BIO USA 2026 파트너 스크래핑 ===")

    tab_id = get_active_tab()
    if not tab_id:
        print("탭 없음 또는 만료 — 세션 재주입 중...")
        tab_id = inject_session()

    print(f"탭: {tab_id}")

    all_companies, seen_names = load_existing()
    done_keywords = {c["search_keyword"] for c in all_companies}
    print(f"기존 수집: {len(all_companies)}개, 완료 키워드: {done_keywords}")

    for keyword in SEARCH_KEYWORDS:
        if keyword in done_keywords:
            print(f"\n[{keyword}] 이미 완료, 스킵")
            continue

        # 탭 살아있는지 확인, 죽으면 재주입
        try:
            get_snapshot(tab_id)
        except Exception:
            print(f"  탭 만료 — 세션 재주입 중...")
            tab_id = inject_session()

        new = search_and_scrape(tab_id, keyword, seen_names, all_companies)
        all_companies.extend(new)
        save_raw(all_companies)
        print(f"  → 키워드 완료 저장 (총 {len(all_companies)}개)")

    print(f"\n=== 총 수집: {len(all_companies)}개 ===")

    filtered = filter_companies(all_companies)
    os.makedirs(WORK_DIR + "/data", exist_ok=True)
    with open(FILTERED_PATH, "w", encoding="utf-8") as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)
    print(f"필터링: {len(filtered)}개 → {FILTERED_PATH}")

    print("\n=== 상위 타깃 기업 (relevance 순) ===")
    for i, c in enumerate(filtered[:30], 1):
        print(f"{i:2}. [{c.get('relevance_score',0)}점] {c['name']}")
        tc = c.get("type_country","")[:60]
        if tc:
            print(f"    {tc}")
        if c.get("description"):
            print(f"    {c['description'][:120]}")


if __name__ == "__main__":
    main()
