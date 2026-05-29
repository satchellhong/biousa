"""complexClusters API 파라미터 확인"""
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
    async with AsyncCamoufox(headless=True) as browser:
        ctx = await browser.new_context(viewport={"width":1920,"height":1080})
        await ctx.add_cookies(load_cookies())
        page = await ctx.new_page()

        async def on_resp(resp):
            if "complexClusters" in resp.url and "favorite" not in resp.url:
                print(f"\nFULL URL: {resp.url}")
                try:
                    body = await resp.json()
                    clusters = body.get("result",{}).get("clusters",[])
                    print(f"clusters: {len(clusters)}")
                    if clusters:
                        print(f"sample: {json.dumps(clusters[0], ensure_ascii=False)[:200]}")
                except: pass

        page.on("response", on_resp)
        await page.goto("https://fin.land.naver.com/map", wait_until="load")
        await asyncio.sleep(4)
        await page.mouse.move(960, 540)
        for _ in range(4):
            await page.mouse.wheel(0, -300)
            await asyncio.sleep(0.8)
        await asyncio.sleep(3)
        await ctx.close()

asyncio.run(main())
