"""Playwright regression checks for the timed power bar.

Requires: pip install playwright; Chromium installed.
Run: python tests/test_power_meter.py
"""
import asyncio
import shutil
from pathlib import Path
from playwright.async_api import async_playwright

HTML = (Path(__file__).resolve().parents[1] / 'casino-noir-standalone.html').read_text(encoding='utf-8')


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, executable_path=shutil.which('chromium'), args=['--no-sandbox'])
        for name, width, height in [('desktop', 1440, 900), ('mobile', 390, 844)]:
            context = await browser.new_context(viewport={'width': width, 'height': height})
            page = await context.new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            await page.route('https://**/*', lambda route: route.abort())
            await page.set_content(HTML, wait_until='domcontentloaded')
            assert await page.locator('#editorPanel').is_hidden()
            assert await page.locator('#powerMeter').get_attribute('role') == 'meter'
            assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            first = await page.evaluate('window.__casinoNoirDebug.power')
            await page.wait_for_timeout(200)
            assert abs(await page.evaluate('window.__casinoNoirDebug.power') - first) > 0.1
            await page.locator('.stage-heading').click()
            assert not await page.evaluate('window.__casinoNoirDebug.isSpinning')

            measurements = []
            for condition in ['< 0.08', '> 0.94']:
                await page.wait_for_function(f'window.__casinoNoirDebug.power {condition}')
                await page.evaluate("document.getElementById('spinHub').click()")
                assert await page.locator('#spinHub').is_disabled()
                locked = await page.evaluate('window.__casinoNoirDebug.power')
                await page.wait_for_timeout(150)
                assert abs(await page.evaluate('window.__casinoNoirDebug.power') - locked) < 0.0001
                await page.wait_for_function('!window.__casinoNoirDebug.isSpinning', timeout=15000)
                result = await page.evaluate('''() => ({
                  power:window.__casinoNoirDebug.lastPower,
                  turns:window.__casinoNoirDebug.lastTurns,
                  duration:window.__casinoNoirDebug.lastDurationMs,
                  winner:window.__casinoNoirDebug.lastWinner,
                  angle:window.__casinoNoirDebug.rotation,
                  count:window.__casinoNoirDebug.config.segments.length
                })''')
                winner = round(-((result['angle'] % 360) + 360) % 360 / (360 / result['count'])) % result['count']
                assert winner == result['winner'], (name, result)
                assert await page.locator('#spinHub').is_enabled()
                measurements.append(result)
            low, high = measurements
            assert low['power'] < 0.15 and high['power'] > 0.88
            assert low['turns'] <= 3 and high['turns'] >= 9
            assert high['duration'] > low['duration'] * 1.5

            await page.locator('#showOnlyWheel').click()
            assert await page.evaluate("document.getElementById('presentationTarget').contains(document.getElementById('powerMeter'))")
            await page.locator('#closePresentation').click()
            assert not errors, errors
            print(f'{name}: PASS – low {low["turns"]} / high {high["turns"]} turns')
            await context.close()

        reduced = await browser.new_context(reduced_motion='reduce')
        page = await reduced.new_page()
        await page.route('https://**/*', lambda route: route.abort())
        await page.set_content(HTML, wait_until='domcontentloaded')
        await page.locator('#spinHub').click()
        await page.wait_for_function('!window.__casinoNoirDebug.isSpinning', timeout=4500)
        assert await page.evaluate('window.__casinoNoirDebug.lastTurns') == 0
        assert 'Ergebnis:' in await page.locator('#statusText').inner_text()
        print('Reduced motion: PASS')
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
