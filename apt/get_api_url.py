"""실제 complexClusters API URL 캡처"""
import asyncio, json
from camoufox.async_api import AsyncCamoufox

COOKIE_FILE = "/Users/seokcholhong/workspace/aws_ftr/naver_fin_cookies.json"

def fix_ss(v):
    return {"no_restriction":"None","lax":"Lax","strict":"Strict","unspecified":"Lax"}.get(v,"Lax")

def load_cookies():
    with open(COOKIE_FILE) as f: raw = json.load(f)
    return [{"name":c["name"],"value":c["value"],"domain":c["domain"],
             "path":c.get("path","/"),"secure":c.get("secure",False),
             "httpOnly":c.get("httpOnly",False),"sameSite":fix_ss(c.get("sameSite","lax"))} for c in raw]

async def main():
    async with AsyncCamoufox(headless=False) as browser:
        ctx = await browser.new_context(viewport={"width":1920,"height":1080})
        await ctx.add_cookies(load_cookies())
        page = await ctx.new_page()

        found_urls = []
        async def on_resp(resp):
            url = resp.url
            if "complex" in url.lower() and "naver" in url:
                print(f"URL: {url}")
                found_urls.append(url)

        page.on("response", on_resp)
        await page.goto("https://fin.land.naver.com/map", wait_until="load")
        await asyncio.sleep(5)

        # 마우스 이동으로 지도 재호출 유도
        await page.mouse.move(960, 540)
        for _ in range(3):
            await page.mouse.wheel(0, -300)
            await asyncio.sleep(1)

        await asyncio.sleep(5)
        print(f"\n캡처된 URL 수: {len(found_urls)}")

        # 10초 대기
        await asyncio.sleep(10)
        await ctx.close()

asyncio.run(main())
