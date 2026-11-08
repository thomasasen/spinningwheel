"""Regression for compact pointer and outward label/icon placement."""
import asyncio
import json
import shutil
from pathlib import Path
from playwright.async_api import async_playwright

HTML = (Path(__file__).resolve().parents[1] / 'casino-noir-standalone.html').read_text(encoding='utf-8')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, executable_path=shutil.which('chromium'), args=['--no-sandbox', '--disable-dev-shm-usage'])
        for device, viewport in [('desktop', {'width':1440, 'height':900}), ('mobile', {'width':390, 'height':844})]:
            ctx = await browser.new_context(viewport=viewport, reduced_motion='reduce')
            page = await ctx.new_page()
            await page.route('https://**/*', lambda route: route.abort())
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            await page.set_content(HTML, wait_until='domcontentloaded')
            arrow = await page.evaluate("""() => {const b=document.getElementById('fixedPointer').getBBox();return {w:b.width,h:b.height,bottom:b.y+b.height}}""")
            assert arrow['w'] < 50 and arrow['h'] < 85 and arrow['bottom'] <= 81, arrow
            assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth'), device
            for n in (2,8,12,20,21,36,72):
                payload = {'segments':[{'label':f'Gewinn {i+1}', 'icon':'star', 'showLabel':True, 'showIcon':True,
                                       'color':'#981439' if i%2==0 else '#171218'} for i in range(n)],
                           'duration':3, 'coast':100, 'sound':False, 'palette':'noir'}
                await page.locator('#importFile').set_input_files({'name':'wheel.json', 'mimeType':'application/json',
                                                                  'buffer':json.dumps(payload).encode()})
                await page.wait_for_function('(n)=>window.__casinoNoirDebug.config.segments.length===n',arg=n)
                radii = await page.evaluate("""() => [...document.querySelectorAll('#rotatingWheel > g[transform]')]
                  .map(g=>{const m=g.getAttribute('transform').match(/translate\(([-.\d]+) ([-.\d]+)\)/);
                           return m ? Math.hypot(+m[1]-320,+m[2]-320) : null}).filter(x=>x!==null)""")
                expected = 190 if n<=8 else 198 if n<=12 else 204 if n<=20 else 220
                assert len(radii)==n and all(abs(x-expected)<.02 for x in radii), (n,radii[:4])
                await page.evaluate('()=>{window.crypto.getRandomValues=a=>{a[0]=0;return a}}')
                await page.locator('#spinHub').click()
                await page.wait_for_function('!window.__casinoNoirDebug.isSpinning',timeout=7000)
                assert await page.evaluate('window.__casinoNoirDebug.lastWinner')==0
                if n<=20:
                    gap=await page.evaluate("""() => {
                      const g=document.querySelector('#rotatingWheel > g[transform]');
                      return g.getBoundingClientRect().top-document.getElementById('fixedPointer').getBoundingClientRect().bottom;
                    }""")
                    assert gap>=-1,(device,n,gap)
            assert not errors, errors
            print(device, 'PASS: compact pointer, outward labels, correct winning sector')
            await ctx.close()
        await browser.close()

if __name__=='__main__':
    asyncio.run(main())
