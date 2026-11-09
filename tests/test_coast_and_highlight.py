"""Browser regression for 30s maximum, late braking, winner spotlight and persistence."""
import asyncio, json, shutil
from pathlib import Path
from playwright.async_api import async_playwright

BASE=Path(__file__).resolve().parents[1]
HTML=(BASE/'casino-noir-standalone.html').read_text(encoding='utf-8')

async def page_with_app(browser, viewport, reduced_motion='reduce', stored=None):
    context=await browser.new_context(viewport=viewport,reduced_motion=reduced_motion,accept_downloads=True)
    page=await context.new_page()
    await page.route('https://**/*',lambda route:route.abort())
    if stored is not None:
        # set_content doesn't navigate, so add_init_script alone does not run.
        await page.evaluate('''(data) => {
            window.__mockStorage = {'casino-noir-wheel-studio-v1': JSON.stringify(data)};
            Object.defineProperty(window, 'localStorage', {configurable:true,value:{
                getItem(k){return window.__mockStorage[k] ?? null},
                setItem(k,v){window.__mockStorage[k]=String(v)},
                removeItem(k){delete window.__mockStorage[k]}
            }});
        }''',stored)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    await page.set_content(HTML,wait_until='domcontentloaded')
    return context,page,errors

async def main():
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,executable_path=shutil.which('chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
        for name,viewport in [('desktop',{'width':1440,'height':900}),('mobile',{'width':390,'height':844})]:
            context,page,errors=await page_with_app(browser,viewport)
            assert await page.locator('#editorPanel').is_hidden()
            assert await page.locator('#spinDuration').get_attribute('max')=='30'
            await page.locator('#toggleEditor').click()
            await page.locator('#spinDuration').fill('30')
            await page.locator('#coastIntensity').fill('100')
            assert await page.locator('#durationLabel').text_content()=='30 s'
            assert await page.locator('#coastLabel').text_content()=='100 %'
            assert await page.evaluate('window.__casinoNoirDebug.config.duration')==30
            assert await page.evaluate('window.__casinoNoirDebug.config.coast')==100
            assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth'),name
            # High suspense should leave substantially more rotation in the last 10%.
            curve=await page.evaluate('''() => { const fn=window.__casinoNoirDebug.spinEase; return [fn(.9,0),fn(.9,100),fn(1,100),fn(0,100)]; }''')
            assert curve[0]>curve[1]+0.03 and curve[2]==1 and curve[3]==0,curve
            await page.locator('#closeEditor').click()
            # Choose a shorter duration for real spin tests; the 30 s limit is covered above.
            await page.locator('#toggleEditor').click()
            await page.locator('#spinDuration').fill('3')
            await page.locator('#closeEditor').click()
            await page.locator('#spinHub').click()
            await page.wait_for_function('!window.__casinoNoirDebug.isSpinning',timeout=3000)
            result=await page.evaluate('''() => ({idx:window.__casinoNoirDebug.lastWinner,
                angle:window.__casinoNoirDebug.rotation,
                count:window.__casinoNoirDebug.config.segments.length,
                highlighted:window.__casinoNoirDebug.highlightedWinner,
                coast:window.__casinoNoirDebug.lastCoast,
                exponent:window.__casinoNoirDebug.lastEasingExponent})''')
            expected=round(-((result['angle']%360)+360)%360/(360/result['count']))%result['count']
            assert expected==result['idx']==result['highlighted'],result
            assert result['coast']==100 and abs(result['exponent']-1.35)<.001,result
            assert await page.locator('#winnerHighlight.is-visible > .winner-highlight-surface').count()==1
            assert await page.locator('#statusText').inner_text()!=''
            dest=BASE.parent/f'casino-noir-coast-{name}.png'
            await page.screenshot(path=str(dest),full_page=True)
            # Highlight is cleared immediately on the next spin.
            await page.locator('#spinHub').click()
            assert await page.locator('#winnerHighlight.is-visible').count()==0
            await page.wait_for_function('!window.__casinoNoirDebug.isSpinning',timeout=3000)
            await page.locator('#toggleEditor').click()
            await page.locator('#addSegment').click()
            assert await page.locator('#winnerHighlight.is-visible').count()==0
            assert not errors,errors
            # Check JSON export has coast property.
            async with page.expect_download() as download_future:
                await page.locator('#exportJson').click()
            dl=await download_future.value
            data=json.loads(Path(await dl.path()).read_text())
            assert data['coast']==100 and data['duration']==3
            print(name,'PASS','winner',result['idx'],'slow curve',curve,'width',await page.evaluate('document.documentElement.scrollWidth'))
            await context.close()
        # Old saved configs without coast get the safe default.
        old={'segments':[{'label':'Gewinn','icon':'star','showLabel':True,'showIcon':True,'color':'#981439'}], 'duration':12,'sound':False,'palette':'noir'}
        context,page,errors=await page_with_app(browser,{'width':900,'height':650},stored=old)
        assert await page.evaluate('window.__casinoNoirDebug.config.coast')==65
        assert await page.evaluate('window.__casinoNoirDebug.config.duration')==12
        assert not errors,errors
        await context.close()
        # Bounds for imported settings and removal of highlight after reset.
        context,page,errors=await page_with_app(browser,{'width':900,'height':650})
        for v,expected in [(999,30),(-20,3)]:
            config={**old,'duration':v,'coast':999}
            await page.locator('#importFile').set_input_files({'name':'test.json','mimeType':'application/json','buffer':json.dumps(config).encode()})
            await page.wait_for_timeout(200)
            actual=await page.evaluate('''() => ({
                duration:window.__casinoNoirDebug.config.duration,
                coast:window.__casinoNoirDebug.config.coast,
                toast:document.getElementById('toast').textContent,
                importValue:document.getElementById('importFile').value,
                workspace:JSON.parse(localStorage.getItem('casino-noir-wheel-studio-workspace-v2')||'null')?.items?.length
            })''')
            print('Legacy import diagnostic',v,'expected',expected,'actual',actual,flush=True)
            assert actual['duration']==expected,(v,expected,actual)
            assert actual['coast']==100,actual
        print('Legacy config, import bounds: PASS')
        await context.close()
        await browser.close()

if __name__=='__main__':asyncio.run(main())