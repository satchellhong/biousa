"""
디버그 스크립트 — 종로구 하나만 테스트, 응답 URL 전체 출력
"""
import asyncio
import json
from pathlib import Path
from camoufox.async_api import AsyncCamoufox

COOKIE_FILE = "/Users/seokcholhong/workspace/aws_ftr/naver_fin_cookies.json"

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

async def main():
    cookies = load_cookies()
    captured = {}

    async with AsyncCamoufox(headless=False) as browser:
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        await context.add_cookies(cookies)
        page = await context.new_page()

        # 모든 응답 URL 출력
        async def on_response(resp):
            url = resp.url
            if "land.naver" in url or "naver.com/api" in url:
                print(f"RESP: {url[:100]}")
            if "complexClusters" in url:
                print(f"*** complexClusters hit! ***")
                try:
                    body = await resp.json()
                    clusters = body.get("result", {}).get("clusters", [])
                    print(f"*** clusters: {len(clusters)} ***")
                    for c in clusters[:3]:
                        captured[str(c.get("complexNumber",""))] = c
                except Exception as e:
                    print(f"*** parse error: {e} ***")

        page.on("response", on_response)

        print("페이지 로딩...")
        await page.goto("https://fin.land.naver.com/map", wait_until="load")
        await asyncio.sleep(5)

        print("\n--- 검색창 클릭 ---")
        await page.mouse.click(250, 23)
        await asyncio.sleep(0.3)
        await page.keyboard.press("Control+a")
        await page.keyboard.type("종로구")
        await asyncio.sleep(3)

        items = await page.query_selector_all("li[class*='item']")
        print(f"자동완성 항목: {len(items)}개")
        for item in items[:5]:
            vis = await item.is_visible()
            if vis:
                txt = await item.inner_text()
                print(f"  visible: {txt[:40]}")
                await item.click()
                break
        else:
            print("visible 항목 없음 — 엔터")
            await page.keyboard.press("Enter")

        await asyncio.sleep(4)

        print("\n--- zoom-in 8회 ---")
        cx, cy = 960, 540
        await page.mouse.move(cx, cy)
        for i in range(8):
            await page.mouse.wheel(0, -400)
            await asyncio.sleep(0.8)
            print(f"  wheel {i+1}")

        await asyncio.sleep(3)
        print(f"\n캡처된 단지: {len(captured)}개")

        # 추가 pan
        print("\n--- pan 테스트 ---")
        for dx, dy in [(300, 0), (-600, 0), (300, 300)]:
            await page.mouse.move(cx, cy)
            await page.mouse.down()
            await page.mouse.move(cx - dx, cy - dy, steps=8)
            await page.mouse.up()
            await asyncio.sleep(2.5)

        await asyncio.sleep(3)
        print(f"\n최종 캡처: {len(captured)}개")
        for k, v in list(captured.items())[:5]:
            print(f"  {k}: {v.get('totalHouseholdNumber')}세대, {v.get('baseSpace')}㎡")

        await asyncio.sleep(10)
        await context.close()

asyncio.run(main())
