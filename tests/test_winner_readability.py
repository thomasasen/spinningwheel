"""Regressions: a winner's icon, label or segment number is upright at 12 o'clock."""
import asyncio, json, math
from pathlib import Path
from playwright.async_api import async_playwright

BASE=Path(__file__).resolve().parents[1]
HTML=(BASE/'casino-noir-standalone.html').read_text(encoding='utf-8')

def config(n):
    return {'segments':[{'label':f'Gewinn {i+1}', 'icon':'star','showLabel':True,'showIcon':True,'color':'#971539' if i%2==0 else '#191318'} for i in range(n)],'duration':3,'sound':False,'palette':'noir'}

async def check(page,n,winner):
    await page.evaluate('''(val) => { window.crypto.getRandomValues = a => { a[0] = val; return a; }; }''', int((winner+0.25)/n*4294967296))
    await page.locator('#spinHub').click()
    await page.wait_for_function('!window.__casinoNoirDebug.isSpinning',timeout=4000)
    data=await page.evaluate('''(n) => {
        const winner=window.__casinoNoirDebug.lastWinner;
        const wheelRotation=window.__casinoNoirDebug.rotation;
        const groups=[...document.querySelectorAll('#rotatingWheel g[transform]')].filter(g=>g.querySelector(':scope > title')||g.querySelector(':scope > text.face-number'));
        const target=groups[winner];
        const segmentAngle=Number(target.getAttribute('transform').match(/rotate\\(([^)]+)\\)/)[1]);
        return {winner,wheelRotation,segmentAngle,count:groups.length,hasLabel:!!target.querySelector('text.face-label'),hasIcon:!!target.querySelector('text.face-icon, text.face-fallback'),hasNumber:!!target.querySelector('text.face-number')};
    }''',n)
    assert data['winner']==winner,(n,winner,data)
    assert data['count']==n,(n,winner,data)
    orientation=(data['wheelRotation']+data['segmentAngle'])%360
    assert min(orientation,360-orientation)<.0005,(n,winner,orientation,data)
    if n<=20:assert data['hasLabel'] and data['hasIcon'],data
    else:assert data['hasNumber'],data
    return data

async def main():
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,executable_path=shutil.which('chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
        page=await browser.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce')
        await page.route('https://fonts.googleapis.com/**',lambda r:r.abort())
        await page.route('https://fonts.gstatic.com/**',lambda r:r.abort())
        await page.evaluate("""() => {window.__storage={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem(k){return window.__storage[k] ?? null},setItem(k,v){window.__storage[k]=String(v)}}});}""")
        errors=[];page.on('pageerror',lambda e: errors.append(str(e)))
        await page.set_content(HTML,wait_until='domcontentloaded')
        for n in [1,2,3,5,8,12,16,20,21,36,72]:
            await page.locator('#importFile').set_input_files({'name':'wheel.json','mimeType':'application/json','buffer':json.dumps(config(n)).encode()})
            await page.wait_for_function('(n) => document.querySelectorAll(".segment-card").length===n', arg=n,timeout=10000)
            for winner in sorted({0,n//2,n-1}):
                await check(page,n,winner)
                if n==8 and winner==4:
                    await page.screenshot(path='/mnt/data/casino-noir-gewinner-oben.png',full_page=True)
            print(f'{n} segments: all selected winning labels upright at 12 o\'clock')
        assert not errors,errors
        await browser.close()

if __name__=='__main__':asyncio.run(main())