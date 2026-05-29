"""complexClusters 요청 body 캡처"""
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

        async def on_req(req):
            if "complexClusters" in req.url and "favorite" not in req.url:
                print(f"\nMETHOD: {req.method}")
                print(f"URL: {req.url}")
                headers = await req.all_headers()
                print(f"Headers (relevant):")
                for k,v in headers.items():
                    if k.lower() in ['content-type','cookie','referer','x-csrf','authorization']:
                        print(f"  {k}: {v[:100]}")
                try:
                    body = req.post_data
                    print(f"BODY: {body}")
                except: pass

        page.on("request", on_req)
        await page.goto("https://fin.land.naver.com/map", wait_until="load")
        await asyncio.sleep(4)
        await page.mouse.move(960,540)
        for _ in range(4):
            await page.mouse.wheel(0,-300)
            await asyncio.sleep(0.8)
        await asyncio.sleep(3)
        await ctx.close()

asyncio.run(main())
