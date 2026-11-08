"""Winner effects and synthesized sound selection regression; run with Python Playwright."""
import asyncio
import json
import shutil
from pathlib import Path

from playwright.async_api import async_playwright

BASE = Path(__file__).resolve().parents[1]
HTML = (BASE / 'casino-noir-standalone.html').read_text(encoding='utf-8')
EFFECTS = ('outline', 'spotlight', 'lift', 'lights', 'celebration', 'cinematic')
SOUNDS = ('off', 'soft', 'bell', 'chime', 'jackpot', 'fanfare')


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, executable_path=shutil.which('chromium'), args=['--no-sandbox', '--disable-dev-shm-usage'])
        for name, viewport in (('desktop', {'width': 1440, 'height': 900}), ('mobile', {'width': 390, 'height': 844})):
            context = await browser.new_context(viewport=viewport, reduced_motion='reduce', accept_downloads=True)
            page = await context.new_page()
            await page.route('https://**/*', lambda route: route.abort())
            errors = []
            page.on('pageerror', lambda err: errors.append(str(err)))
            await page.set_content(HTML, wait_until='domcontentloaded')
            await page.locator('#toggleEditor').click()
            assert await page.locator('#winnerEffect option').count() == 6
            assert await page.locator('#winnerSound option').count() == 6
            assert await page.locator('#winnerStrength option').count() == 3
            for mode in EFFECTS:
                await page.locator('#winnerEffect').select_option(mode)
                await page.locator('#previewWinnerEffect').click()
                assert await page.locator('#presentation').is_hidden(), mode
                assert await page.locator('#editorBackdrop').is_visible(), mode
                assert await page.locator('#editorBackdrop').evaluate('(el)=>getComputedStyle(el).backdropFilter')=='none'
                assert await page.locator('#editorPanel').is_visible(), mode
                assert await page.locator('#winnerHighlight.is-visible').count() == 1, mode
                assert await page.locator('#winnerHighlight').get_attribute('data-effect') == mode
                assert await page.locator('#winnerHighlight > .winner-highlight-surface').count() == 1
                expected = {
                    'outline': (0, 0, 0, 0),
                    'spotlight': (7, 0, 0, 0),
                    'lift': (0, 1, 0, 0),
                    'lights': (0, 0, 1, 0),
                    'celebration': (0, 0, 0, 1),
                    'cinematic': (7, 0, 1, 0),
                }[mode]
                values = (
                    await page.locator('.winner-shade-sector').count(),
                    await page.locator('.winner-lift').count(),
                    int(await page.locator('.winner-stud').count() > 0),
                    int(await page.locator('.winner-particle').count() > 0),
                )
                assert values == expected, (mode, values, expected)
                await page.keyboard.press('Escape')
                assert await page.locator('#editorPanel').is_visible(), mode
            for strength in ('subtle','refined','show'):
                await page.locator('#winnerStrength').select_option(strength)
                await page.locator('#previewWinnerEffect').click()
                assert await page.locator('#winnerHighlight').get_attribute('data-strength') == strength
                await page.keyboard.press('Escape')
            for mode in SOUNDS:
                await page.locator('#winnerSound').select_option(mode)
                await page.locator('#previewWinnerSound').click()
                assert await page.evaluate('window.__casinoNoirDebug.config.winnerSound') == mode
            await page.locator('#winnerEffect').select_option('cinematic')
            await page.locator('#winnerStrength').select_option('refined')
            await page.locator('#winnerSound').select_option('chime')
            async with page.expect_download() as dw:
                await page.locator('#exportJson').click()
            data = json.loads(Path(await (await dw.value).path()).read_text())
            assert data['winnerEffect'] == 'cinematic' and data['winnerStrength'] == 'refined' and data['winnerSound'] == 'chime'
            await page.locator('#closeEditor').click()
            # Spin, result must line up and inherit chosen effect.
            await page.locator('#spinHub').click()
            await page.wait_for_function('!window.__casinoNoirDebug.isSpinning', timeout=6000)
            winner = await page.evaluate('window.__casinoNoirDebug.lastWinner')
            assert await page.evaluate('window.__casinoNoirDebug.highlightedWinner') == winner
            assert await page.locator('#winnerHighlight').get_attribute('data-effect') == 'cinematic'
            assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth'), name
            await page.screenshot(path=str(BASE.parent / f'casino-noir-winner-options-{name}.png'),full_page=True)
            assert not errors,errors
            await context.close()
            print(name,'six modes + strength + sound preview + persistence + spin: PASS')
        # Imported legacy configurations keep safe defaults.
        context = await browser.new_context(viewport={'width': 1100, 'height': 800})
        page = await context.new_page()
        await page.route('https://**/*', lambda route: route.abort())
        await page.set_content(HTML)
        legacy={'segments':[{'label':'Gewinn','icon':'star','showLabel':True,'showIcon':True,'color':'#981439'}], 'duration':3,'coast':75,'sound':False,'palette':'noir'}
        await page.locator('#importFile').set_input_files({'name':'old.json','mimeType':'application/json','buffer':json.dumps(legacy).encode()})
        await page.wait_for_function('window.__casinoNoirDebug.config.segments.length === 1')
        cfg=await page.evaluate('window.__casinoNoirDebug.config')
        assert (cfg['winnerEffect'],cfg['winnerStrength'],cfg['winnerSound'])==('cinematic','refined','chime'),cfg
        assert cfg['sound'] is False
        for invalid in ({'winnerEffect':'bad','winnerStrength':'bogus','winnerSound':'foobar'},):
            await page.locator('#importFile').set_input_files({'name':'invalid.json','mimeType':'application/json','buffer':json.dumps({**legacy,**invalid}).encode()})
            await page.wait_for_timeout(100)
            cfg=await page.evaluate('window.__casinoNoirDebug.config')
            assert (cfg['winnerEffect'],cfg['winnerStrength'],cfg['winnerSound'])==('cinematic','refined','chime')
        # Geometry stress with 1 and 72 sectors for each animation.
        for n in (1,3,20,72,90):
            segs=[dict(label=f'Gewinn {k}',icon='star',showLabel=True,showIcon=True,color='#981439' if k%2==0 else '#181318') for k in range(n)]
            await page.locator('#importFile').set_input_files({'name':'many.json','mimeType':'application/json','buffer':json.dumps({**legacy,'segments':segs}).encode()})
            await page.wait_for_function('(n) => window.__casinoNoirDebug.config.segments.length === n',arg=n)
            for mode in EFFECTS:
                await page.evaluate('([mode,n]) => {const d=window.__casinoNoirDebug;d.config.winnerEffect=mode;d.showWinnerHighlight(n-1)}',[mode,n])
                assert await page.locator('#winnerHighlight.is-visible').count()==1,(n,mode)
                assert await page.locator('#winnerHighlight-sentinel').count()==0
        print('legacy, invalid input, 1..90 geometry: PASS')
        await context.close()
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())