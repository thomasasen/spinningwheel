"""Semantic icon search ranking and selection, including shirt -> apparel + laundry."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/'casino-noir-standalone.html').read_text(encoding='utf-8')
async def main():
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True, args=['--no-sandbox','--disable-dev-shm-usage'])
        for width in (1440,390):
            context=await browser.new_context(viewport={'width':width,'height':850})
            page=await context.new_page()
            await page.route('https://**/*',lambda route:route.abort())
            errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            await page.set_content(HTML,wait_until='domcontentloaded')
            await page.locator('#toggleEditor').click()
            await page.locator('.segment-icon-btn').first.click()
            await page.wait_for_function('window.__casinoNoirDebug.iconSearchMetadataReady')
            assert await page.evaluate('window.__casinoNoirDebug.iconSearchMetadataCount')>=3800
            for query,expected in [('shirt',['apparel','laundry']),('laundrey',['laundry']),('washing',['laundry']),('clothing',['apparel','laundry'])]:
                await page.locator('#iconSearch').fill(query)
                for name in expected:
                    assert await page.locator(f'.symbol-choice[data-icon="{name}"]').count()==1,(width,query,name)
            await page.locator('#iconSearch').fill('shirt')
            await page.locator('.symbol-choice[data-icon="laundry"]').click()
            assert await page.evaluate('window.__casinoNoirDebug.config.segments[0].icon')=='laundry'
            assert not errors,errors
            print(width,'PASS: semantic tags, typo alias, icon selection')
            await context.close()
        await browser.close()
if __name__=='__main__':
    asyncio.run(main())
