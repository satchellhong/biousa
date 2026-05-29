#!/usr/bin/env /opt/homebrew/Caskroom/miniconda/base/bin/python
"""
partner.bio.org 세션 주입 및 탭 생성
"""
import json
import time
import urllib.request

BASE = "http://localhost:9377"
USER = "biousa-agent"
WORK_DIR = "/Users/seokcholhong/workspace/biousa"


def api(method, path, body=None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def main():
    # 1. 쿠키 주입
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

    result = api("POST", "/sessions/biousa-agent/cookies", {"cookies": cookies})
    print("쿠키 주입:", result)

    # 2. 탭 생성
    tab = api("POST", "/tabs", {"userId": USER, "sessionKey": "scrape1", "url": "https://partner.bio.org/conference/86/search"})
    tab_id = tab["tabId"]
    print("탭 생성:", tab_id)

    # 3. localStorage 주입 (즉시)
    with open(WORK_DIR + "/auth_data.json") as f:
        auth = json.load(f)

    ls = auth["localStorage"]
    lines = []
    for k, v in ls.items():
        lines.append("localStorage.setItem({},{});".format(json.dumps(k), json.dumps(v)))

    script = "(function(){" + "".join(lines) + "window.location.href='https://partner.bio.org/conference/86/search';})()"

    time.sleep(1)
    result = api("POST", f"/tabs/{tab_id}/evaluate", {"expression": script, "userId": USER})
    print("localStorage 주입:", result)

    # 4. 로딩 대기
    print("로딩 대기 중 (8초)...")
    time.sleep(8)

    # 5. 확인
    req = urllib.request.Request(BASE + f"/tabs/{tab_id}/snapshot?userId={USER}")
    with urllib.request.urlopen(req) as r:
        snap = json.loads(r.read())

    url = snap.get("url", "")
    print("현재 URL:", url)

    if "partner.bio.org/conference/86/search" in url:
        print("로그인 성공!")
        # tab_id 저장
        with open(WORK_DIR + "/src/active_tab.txt", "w") as f:
            f.write(tab_id)
        print(f"탭 ID 저장: src/active_tab.txt ({tab_id})")
    else:
        print("로그인 실패 — auth_data.json 갱신 필요")


if __name__ == "__main__":
    main()
