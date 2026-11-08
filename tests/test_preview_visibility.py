"""Winner-effect preview removes drawer blur for four seconds, then restores settings."""
import asyncio
import shutil
from pathlib import Path
from playwright.async_api import async_playwright

BASE=Path(__file__).resolve().parents[1]
HTML=(BASE/'casino-noir-standalone.html').read_text(encoding='utf-8')
EFFECTS=('outline','spotlight','lift','lights','celebration','cinematic')

async def main():
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,executable_path=shutil.which('chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
        for name,viewport in [('desktop',{'width':1440,'height':900}),('mobile',{'width':390,'height':844})]:
            ctx=await browser.new_context(viewport=viewport,reduced_motion='reduce')
            page=await ctx.new_page()
            await page.route('https://**/*', lambda route:route.abort())
            errors=[]
            page.on('pageerror',lambda err:errors.append(str(err)))
            await page.set_content(HTML,wait_until='domcontentloaded')
            await page.locator('#toggleEditor').click()
            assert await page.locator('#editorPanel').is_visible()
            assert 'blur' in await page.locator('#editorBackdrop').evaluate('(el)=>getComputedStyle(el).backdropFilter')
            for effect in EFFECTS:
                await page.locator('#winnerEffect').select_option(effect)
                rotation_before=await page.evaluate('window.__casinoNoirDebug.rotation')
                await page.locator('#previewWinnerEffect').click()
                assert await page.locator('#presentation').is_hidden(),(name,effect)
                assert await page.locator('#editorPanel').is_visible(),(name,effect)
                assert await page.locator('#editorBackdrop').is_visible(),(name,effect)
                assert await page.locator('#editorBackdrop').evaluate('(el)=>getComputedStyle(el).backdropFilter')=='none'
                assert await page.locator('#editorBackdrop').evaluate('(el)=>getComputedStyle(el).backgroundColor')=='rgba(0, 0, 0, 0)'
                assert await page.locator('#wheelAssembly').evaluate('(el)=>el.parentElement.classList.contains("wheel-stage")')
                assert await page.locator('body').evaluate('(el)=>el.classList.contains("editor-open")')
                assert await page.locator('#winnerHighlight.is-visible').count()==1
                assert await page.locator('#winnerHighlight').get_attribute('data-effect')==effect
                assert await page.locator('#spinHub').is_disabled()
                assert await page.evaluate('window.__casinoNoirDebug.rotation')==rotation_before
                if effect=='outline':
                    await page.screenshot(path=str(BASE/f'effect-preview-{name}.png'))
                    await page.wait_for_timeout(4300)
                else:
                    await page.keyboard.press('Escape')
                assert await page.locator('#editorPanel').is_visible(),(name,effect)
                assert await page.locator('#editorBackdrop').is_visible(),(name,effect)
                assert 'blur' in await page.locator('#editorBackdrop').evaluate('(el)=>getComputedStyle(el).backdropFilter')
                assert await page.evaluate('document.activeElement.id')=='previewWinnerEffect'
                assert not await page.locator('#spinHub').is_disabled()
                assert await page.evaluate('window.__casinoNoirDebug.highlightedWinner') is None
            await page.locator('#closeEditor').click()
            await page.locator('#showOnlyWheel').click()
            assert await page.locator('#presentation').is_visible()
            await page.locator('#closePresentation').click()
            assert await page.locator('#presentation').is_hidden()
            assert not errors,errors
            await ctx.close()
            print(name,'PASS: 6 styles, four-second unblur, Escape, focus, untouched wheel')
        await browser.close()

if __name__=='__main__':
    asyncio.run(main())
