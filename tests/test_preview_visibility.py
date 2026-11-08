"""Regression: effect preview shows a clear wheel and restores settings on desktop/mobile."""
import asyncio
import shutil
from pathlib import Path
from playwright.async_api import async_playwright

HTML=(Path(__file__).resolve().parents[1]/'casino-noir-standalone.html').read_text(encoding='utf-8')
EFFECTS=('outline','spotlight','lift','lights','celebration','cinematic')

async def main():
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,executable_path=shutil.which('chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
        for name,viewport in [('desktop',{'width':1440,'height':900}),('mobile',{'width':390,'height':844})]:
            ctx=await browser.new_context(viewport=viewport)
            page=await ctx.new_page()
            await page.route('https://**/*', lambda route: route.abort())
            errors=[]
            page.on('pageerror',lambda e: errors.append(str(e)))
            await page.set_content(HTML,wait_until='domcontentloaded')
            await page.locator('#toggleEditor').click()
            for mode in EFFECTS:
                await page.locator('#winnerEffect').select_option(mode)
                await page.locator('#previewWinnerEffect').click()
                assert await page.locator('#presentation').is_visible(), (name,mode)
                assert await page.locator('#editorPanel').is_hidden(), (name,mode)
                assert await page.locator('#editorBackdrop').is_hidden(), (name,mode)
                assert await page.locator('#winnerHighlight.is-visible').count()==1
                assert await page.locator('#winnerHighlight').get_attribute('data-effect')==mode
                assert 'Zurück zur Konfiguration' in await page.locator('#closePresentation').inner_text()
                await page.locator('#closePresentation').click()
                assert await page.locator('#editorPanel').is_visible(), (name,mode)
                assert await page.evaluate('document.activeElement.id')=='previewWinnerEffect'
            await page.locator('#closeEditor').click()
            await page.locator('#showOnlyWheel').click()
            assert await page.locator('#closePresentation').inner_text()=='✕ Schließen'
            await page.locator('#closePresentation').click()
            assert await page.locator('#editorPanel').is_hidden()
            assert not errors,errors
            await ctx.close()
            print(name,'PASS: all six clear previews, return to editor, normal presentation')
        await browser.close()

if __name__=='__main__':
    asyncio.run(main())
