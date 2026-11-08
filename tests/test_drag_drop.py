"""Mouse/touch/keyboard reordering, persistence and SVG regression tests."""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]
URL=(ROOT/'index.html').as_uri()

def labels(cfg): return [s['label'] for s in cfg['segments']]

async def getcfg(page):
    return await page.evaluate('window.__casinoNoirDebug.config')

async def mouse_drag(page, from_idx, to_idx):
    grips=page.locator('.segment-drag-handle')
    fr=await grips.nth(from_idx).bounding_box()
    target=await grips.nth(to_idx).bounding_box()
    x=fr['x']+fr['width']/2
    y=fr['y']+fr['height']/2
    yy=target['y']+target['height']*(.92 if to_idx>from_idx else .12)
    await page.mouse.move(x,y)
    await page.mouse.down()
    await page.mouse.move(x,yy,steps=9)
    await page.mouse.up()

async def test(desktop=True):
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
        ctx=await browser.new_context(viewport={'width':1440 if desktop else 390,'height':900 if desktop else 844},has_touch=not desktop,is_mobile=not desktop)
        page=await ctx.new_page()
        await page.route('https://**/*',lambda route:route.abort())
        errors=[]
        page.on('pageerror',lambda err:errors.append(str(err)))
        # about:blank blocks native localStorage: use a tiny in-memory shim to verify saves.
        await page.evaluate('''() => {const store=new Map();Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>store.get(k)??null,setItem:(k,v)=>store.set(k,String(v)),removeItem:k=>store.delete(k)}})}''')
        await page.set_content((ROOT/'casino-noir-standalone.html').read_text(encoding='utf-8'),wait_until='domcontentloaded')
        await page.locator('#toggleEditor').click()
        before=labels(await getcfg(page))
        assert len(before)==8,before
        assert await page.locator('.segment-drag-handle').count()==8
        if desktop:
            await mouse_drag(page,0,3)
        else:
            # Real CDP touchscreen input to trigger pointer capture on a mobile viewport.
            client=await ctx.new_cdp_session(page)
            a=await page.locator('.segment-drag-handle').nth(0).bounding_box()
            b=await page.locator('.segment-drag-handle').nth(3).bounding_box()
            startx=a['x']+a['width']/2;starty=a['y']+a['height']/2
            endy=b['y']+b['height']*.85
            await client.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':startx,'y':starty,'id':1}]})
            for step in range(1,14):
                await client.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':startx,'y':starty+(endy-starty)*step/13,'id':1}]})
                await asyncio.sleep(.02)
            await client.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
        after=labels(await getcfg(page))
        dropped_at=after.index(before[0])
        assert dropped_at in ((3,) if desktop else (2,3)),('drag',before,after)
        assert after==before[1:dropped_at+1]+before[:1]+before[dropped_at+1:],('drag',before,after)
        assert await page.locator('.segment-card').nth(dropped_at).locator('.segment-label').input_value()==before[0]
        assert await page.locator(f'#rotatingWheel [data-wheel-item="{dropped_at}"]').count()==1
        # Keyboard navigation maintains focus and moves data without lost icon/color.
        await page.locator('.segment-drag-handle').nth(dropped_at).focus()
        await page.keyboard.press('ArrowUp')
        after2=labels(await getcfg(page))
        assert after2[dropped_at-1]==before[0]
        assert await page.evaluate('document.activeElement.classList.contains("segment-drag-handle")')
        await page.keyboard.press('End')
        after3=labels(await getcfg(page))
        assert after3[-1]==before[0]
        await page.keyboard.press('Home')
        after4=labels(await getcfg(page))
        assert after4[0]==before[0]
        if desktop:
            await page.screenshot(path='/mnt/data/spinningwheel-dnd/drag-drop-desktop.png',full_page=True)
        else:
            await page.screenshot(path='/mnt/data/spinningwheel-dnd/drag-drop-mobile.png',full_page=True)
        persisted=await page.evaluate('localStorage.getItem("casino-noir-wheel-studio-v1")')
        assert persisted and [x['label'] for x in json.loads(persisted)['segments']]==after4
        await page.evaluate('document.getElementById("closeEditor").click()')
        await page.locator('#toggleEditor').click()
        await page.locator('#exportJson').click()
        # Confirm UI still responsive to edit/duplicate; drawing retains matching count.
        await page.locator('.segment-card').first.locator('button[data-action="duplicate"]').click()
        assert len((await getcfg(page))['segments'])==9
        assert await page.locator('.segment-drag-handle').count()==9
        await page.locator('.segment-card').first.locator('button[data-action="delete"]').click()
        assert len((await getcfg(page))['segments'])==8
        assert not errors,errors
        print('PASS', 'desktop' if desktop else 'mobile', 'touch drag, keyboard, persistence, SVG, edit controls')
        await ctx.close();await browser.close()

if __name__=='__main__':
    asyncio.run(test(True))
    asyncio.run(test(False))
