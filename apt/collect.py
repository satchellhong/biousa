"""
서울 전 지역 아파트 수집
- camoufox 브라우저 내부에서 fetch()로 complexClusters API 호출
- 서울 전체 bbox 격자 분할
- 중간 저장, 재시작 가능
"""
import asyncio
import json
from pathlib import Path
from camoufox.async_api import AsyncCamoufox

COOKIE_FILE = "/Users/seokcholhong/workspace/aws_ftr/naver_fin_cookies.json"
OUT_DIR = Path(__file__).parent
MERGED_FILE = OUT_DIR / "raw_all.json"
PROGRESS_FILE = OUT_DIR / "progress.json"

API_URL = "https://fin.land.naver.com/front-api/v1/complex/complexClusters"

# 서울 전체 bbox
SEOUL_LAT_MIN, SEOUL_LAT_MAX = 37.41, 37.71
SEOUL_LON_MIN, SEOUL_LON_MAX = 126.77, 127.20

STEP_LAT = 0.018
STEP_LON = 0.030

FILTER = {
    "tradeTypes": ["A1"],
    "realEstateTypes": ["A01"],
    "roomCount": [], "bathRoomCount": [], "optionTypes": [], "oneRoomShapeTypes": [],
    "moveInTypes": [], "filtersExclusiveSpace": False, "floorTypes": [], "directionTypes": [],
    "hasArticlePhoto": False, "isAuthorizedByOwner": False, "parkingTypes": [], "entranceTypes": [],
    "hasArticle": False
}

def fix_ss(v):
    return {"no_restriction": "None", "lax": "Lax", "strict": "Strict", "unspecified": "Lax"}.get(v, "Lax")

def load_cookies():
    with open(COOKIE_FILE) as f:
        raw = json.load(f)
    return [{
        "name": c["name"], "value": c["value"], "domain": c["domain"],
        "path": c.get("path", "/"), "secure": c.get("secure", False),
        "httpOnly": c.get("httpOnly", False),
        "sameSite": fix_ss(c.get("sameSite", "lax")),
    } for c in raw]

def load_json(path, default):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return default

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

def make_grid():
    boxes = []
    lat = SEOUL_LAT_MIN
    while lat < SEOUL_LAT_MAX:
        lon = SEOUL_LON_MIN
        while lon < SEOUL_LON_MAX:
            boxes.append({
                "bottom": round(lat, 6),
                "top": round(lat + STEP_LAT, 6),
                "left": round(lon, 6),
                "right": round(lon + STEP_LON, 6),
            })
            lon = round(lon + STEP_LON * 0.85, 6)
        lat = round(lat + STEP_LAT * 0.85, 6)
    return boxes

async def fetch_box_in_browser(page, box):
    """브라우저 내부 fetch()로 API 호출 — 쿠키 자동 포함"""
    payload = {
        "filter": FILTER,
        "boundingBox": box,
        "precision": 15,
        "userChannelType": "PC"
    }
    args = {"url": API_URL, "payload": payload}
    result = await page.evaluate("""
        async ({url, payload}) => {
            try {
                const resp = await fetch(url, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload),
                    credentials: 'include'
                });
                if (!resp.ok) return {error: resp.status};
                const data = await resp.json();
                return {clusters: data?.result?.clusters || []};
            } catch(e) {
                return {error: e.message};
            }
        }
    """, args)
    return result

async def main():
    merged = load_json(MERGED_FILE, {})
    progress = load_json(PROGRESS_FILE, {})
    grid = make_grid()
    done = set(progress.keys())

    print(f"격자: {len(grid)}개 bbox")
    print(f"기존: {len(merged)}개 단지, 완료: {len(done)}개")

    cookies = load_cookies()

    async with AsyncCamoufox(headless=True) as browser:
        ctx = await browser.new_context(viewport={"width": 1920, "height": 1080})
        await ctx.add_cookies(cookies)
        page = await ctx.new_page()

        print("페이지 로딩...")
        await page.goto("https://fin.land.naver.com/map", wait_until="load")
        await asyncio.sleep(4)

        for i, box in enumerate(grid):
            key = f"{box['bottom']},{box['left']}"
            if key in done:
                continue

            result = await fetch_box_in_browser(page, box)

            if "error" in result:
                err = result["error"]
                if err == 429:
                    print(f"[{i+1}] 429 — 5초 대기", flush=True)
                    await asyncio.sleep(5)
                    # 재시도
                    result = await fetch_box_in_browser(page, box)
                if "error" in result:
                    print(f"[{i+1}] 오류: {result['error']}", flush=True)
                    progress[key] = "error"
                    continue

            clusters = result.get("clusters", [])
            new = 0
            for c in clusters:
                num = str(c.get("complexNumber", ""))
                if num and num not in merged:
                    merged[num] = c
                    new += 1

            progress[key] = {"total": len(clusters), "new": new}

            if new:
                print(f"[{i+1}/{len(grid)}] +{new}신규 (합계 {len(merged)}개) {box['bottom']:.3f},{box['left']:.3f}", flush=True)
            elif (i + 1) % 50 == 0:
                print(f"[{i+1}/{len(grid)}] 합계 {len(merged)}개", flush=True)

            if (i + 1) % 20 == 0:
                save_json(merged, MERGED_FILE)
                save_json(progress, PROGRESS_FILE)

            await asyncio.sleep(0.2)

        save_json(merged, MERGED_FILE)
        save_json(progress, PROGRESS_FILE)
        await ctx.close()

    print(f"\n=== 완료: 총 {len(merged)}개 단지 ===")
    summarize(merged)

def summarize(merged):
    price_ok, no_price = [], []
    for k, v in merged.items():
        h = v.get("totalHouseholdNumber", 0)
        a = v.get("baseSpace", 0)
        p = v.get("realPriceByTradeType", {}).get("A1", {}).get("dealPrice", 0)
        if h < 100 or a < 49:
            continue
        if 0 < p < 600000000:
            price_ok.append((k, v, p))
        elif p == 0:
            no_price.append((k, v))

    print(f"\n조건 충족 (6억 미만): {len(price_ok)}개")
    print(f"조건 충족 (가격 미등록): {len(no_price)}개")
    save_json(
        {"price_ok": {k: v for k, v, _ in price_ok}, "no_price": {k: v for k, v in no_price}},
        OUT_DIR / "candidates_final.json"
    )
    for k, v, p in sorted(price_ok, key=lambda x: x[2]):
        print(f"  {k}: {v['totalHouseholdNumber']}세대 {v['baseSpace']:.0f}㎡ {p//10000}만원 "
              f"({v['coordinates']['xCoordinate']:.4f},{v['coordinates']['yCoordinate']:.4f})")

if __name__ == "__main__":
    asyncio.run(main())
