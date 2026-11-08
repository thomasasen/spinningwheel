from pathlib import Path
base=Path(__file__).resolve().parent
html=(base/'index.html').read_text()
css=(base/'styles.css').read_text()
js=(base/'app.js').read_text()
html=html.replace('<link rel="stylesheet" href="styles.css">',f'<style>\n{css}\n</style>')
html=html.replace('<script defer src="app.js"></script>','')
html=html.replace('</body>',f'<script>\n{js}\n</script>\n</body>')
(base/'casino-noir-standalone.html').write_text(html)
print('standalone',len(html),'bytes')