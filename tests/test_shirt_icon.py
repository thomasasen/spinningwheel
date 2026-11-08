import asyncio, re
from pathlib import Path
from playwright.async_api import async_playwright

BASE=Path(__file__).resolve().parents[1]
entries={'apparel':'ef7b','checkroom':'f19e','dry_cleaning':'ea58','laundry':'e2a8','local_laundry_service':'e54a','styler':'e273','star':'f09a','favorite':'e87e','diamond':'ead5','casino':'eb40','workspace_premium':'e7af','redeem':'e8b1','local_bar':'e540'}
for i in range(4304-len(entries)): entries[f'zz_test_icon_{i:04d}']='e87e'
CAT='\n'.join(f'{k} {v}' for k,v in sorted(entries.items()))+'\n'

async def main():
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu'])
  for width,height,mock_font in [(1440,900,False),(390,844,False),(1440,900,True)]:
   ctx=await browser.new_context(viewport={'width':width,'height':height})
   if mock_font:
    await ctx.add_init_script('document.fonts.load = async () => [{ family: "Material Symbols Rounded" }];')
   async def route_handler(route):
    url=route.request.url
    if '.codepoints' in url:
      await route.fulfill(status=200,headers={'access-control-allow-origin':'*','content-type':'text/plain'},body=CAT)
    elif 'fonts.googleapis.com' in url or 'fonts.gstatic.com' in url:
      await route.abort()
    else:
      await route.continue_()
   await ctx.route('**/*',route_handler)
   page=await ctx.new_page()
   errors=[]
   page.on('pageerror',lambda e:errors.append(str(e)))
   await page.set_content((BASE/'casino-noir-standalone.html').read_text(),wait_until='domcontentloaded')
   await page.wait_for_function('window.__casinoNoirDebug?.iconCatalogCount===4304',timeout=12000)
   # Open the off-canvas configuration before interacting with icon buttons.
   await page.locator('#toggleEditor').click()
   # all icon count and search alias coverage
   await page.locator('.segment-icon-btn').first.click()
   await page.locator('#iconSearch').fill('shirt')
   count=await page.evaluate('window.__casinoNoirDebug.iconMatches')
   matches=await page.evaluate('window.__casinoNoirDebug.iconMatchingNames')
   print('CONFIG',width,mock_font,'search "shirt":',matches,'fontReady:',await page.evaluate('window.__casinoNoirDebug.iconFontReady'))
   assert 'apparel' in matches and 'checkroom' in matches and count>=2
   assert 'shirt' not in matches
   if not mock_font:
    assert await page.locator('button[data-icon="apparel"] svg.icon-fallback-svg').count()==1
   else:
    text=await page.locator('button[data-icon="apparel"] .material-symbols-rounded').text_content()
    assert text == chr(int('ef7b',16)), repr(text)
    assert text!='apparel'
   # custom shirt -> official codepoint icon; must preserve data
   await page.locator('#customIconName').fill('shirt')
   await page.locator('#useCustomIcon').click()
   assert await page.locator('#iconModal').is_hidden()
   cfg=await page.evaluate('window.__casinoNoirDebug.config')
   assert cfg['segments'][0]['icon']=='apparel'
   assert 'shirt' not in await page.locator('#segmentList').inner_text()
   # modal rejects invalid icon instead of rendering raw word
   await page.locator('.segment-icon-btn').first.click()
   await page.locator('#customIconName').fill('not_real_shirt_icon')
   await page.locator('#useCustomIcon').click()
   assert await page.locator('#iconModal').is_visible()
   assert (await page.evaluate('window.__casinoNoirDebug.config.segments[0].icon'))=='apparel'
   # Search in German and with spaces
   await page.locator('#iconSearch').fill('Kleidung')
   assert 'apparel' in await page.evaluate('window.__casinoNoirDebug.iconMatchingNames')
   await page.locator('#iconSearch').fill('T-Shirt')
   assert 'apparel' in await page.evaluate('window.__casinoNoirDebug.iconMatchingNames')
   await page.locator('#iconSearch').fill('')
   assert await page.evaluate('window.__casinoNoirDebug.iconMatches')==4304
   await page.locator('#closeIconModal').click()
   # Check numbered SVG glyph not ligature text
   if mock_font:
    svg_icons=await page.locator('.face-icon').all_text_contents()
    assert svg_icons and all(not re.search('[a-z]{3,}',s) for s in svg_icons),svg_icons
   assert errors==[],errors
   print('PASS',width,height,'font-mocked',mock_font)
   await ctx.close()
  await browser.close()

asyncio.run(main())