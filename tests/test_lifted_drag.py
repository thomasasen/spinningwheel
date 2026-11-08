"""Check physical lift-and-drop mechanics plus cancel and touch input."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

HTML=(Path(__file__).resolve().parents[1]/'casino-noir-standalone.html').read_text(encoding='utf-8')

async def run(browser, mobile):
    ctx=await browser.new_context(viewport={'width':390 if mobile else 1440,'height':844 if mobile else 900},has_touch=mobile,is_mobile=mobile)
    page=await ctx.new_page()
    await page.route('https://**/*',lambda r:r.abort())
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    await page.set_content(HTML,wait_until='domcontentloaded')
    await page.locator('#toggleEditor').click()
    first=page.locator('.segment-drag-handle').first
    a=await first.bounding_box();b=await page.locator('.segment-drag-handle').nth(3).bounding_box()
    x=a['x']+a['width']/2;y=a['y']+a['height']/2;end=b['y']+b['height']*.85
    before=await page.evaluate('window.__casinoNoirDebug.config.segments.map(x=>x.id)')
    if mobile:
        client=await ctx.new_cdp_session(page)
        await client.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y,'id':1}]})
        for i in range(1,14):
            await client.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x+20*i/13,'y':y+(end-y)*i/13,'id':1}]})
            await asyncio.sleep(.015)
    else:
        await page.mouse.move(x,y);await page.mouse.down();await page.mouse.move(x+20,end,steps=12)
    assert await page.locator('.segment-card.is-dragging').count()==1
    assert await page.locator('.segment-drop-placeholder').count()==1
    assert await page.locator('.segment-card.is-dragging').evaluate('(el)=>getComputedStyle(el).position')=='fixed'
    assert await page.evaluate('window.__casinoNoirDebug.config.segments.map(x=>x.id)')==before
    if mobile:await client.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
    else:await page.mouse.up()
    await page.wait_for_timeout(360)
    after=await page.evaluate('window.__casinoNoirDebug.config.segments.map(x=>x.id)')
    assert before!=after
    assert await page.locator('.segment-drop-placeholder').count()==0
    assert await page.locator('.segment-drop-flyer').count()==0
    grip=page.locator('.segment-drag-handle').first
    r=await grip.bounding_box();x=r['x']+r['width']/2;y=r['y']+r['height']/2
    await page.mouse.move(x,y);await page.mouse.down();await page.mouse.move(x+15,y+70,steps=6)
    assert await page.locator('.segment-card.is-dragging').count()==1
    await page.keyboard.press('Escape');await page.mouse.up()
    assert await page.evaluate('window.__casinoNoirDebug.config.segments.map(x=>x.id)')==after
    assert await page.locator('#editorPanel').is_visible()
    assert not errors,errors
    await ctx.close()

async def main():
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        await run(browser,False);await run(browser,True)
        await browser.close()

if __name__=='__main__':asyncio.run(main())
