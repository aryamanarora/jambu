"""Snapshot source for a static build isolated from concurrent workspace builds."""
import shutil
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
DEST=Path('/private/tmp/jambu-telugu-blog-build-20260909')
DEST.mkdir(exist_ok=True)
shutil.copytree(ROOT/'src',DEST/'src',dirs_exist_ok=True)
for name in ['package.json','package-lock.json','tsconfig.json','vite.config.ts','svelte.config.js']:
 shutil.copy2(ROOT/name,DEST/name)
# Compile the whole application but prerender only the affected section. This
# temporary configuration never alters the repository's deployment settings.
config=DEST/'svelte.config.js'
text=config.read_text().replace("prerender: {", "prerender: {\n\t\t\tcrawl: false,\n\t\t\tentries: ['/blogs', '/blogs/telugu-metathesis', '/blogs/shinaic-accent', '/blogs/reading-a-word-in-jambu'],")
config.write_text(text)
# Route-level entries() hooks also enqueue pages independently of crawl. Disable
# prerendering outside /blogs in this disposable copy; client routes still compile.
for route in (DEST/'src/routes').rglob('+*.ts'):
 if 'blogs' not in route.relative_to(DEST/'src/routes').parts:
  content=route.read_text()
  content=content.replace('export const prerender = true', 'export const prerender = false')
  route.write_text(content)
for name in ['node_modules','static','.dbwork']:
 link=DEST/name
 if not link.exists():link.symlink_to(ROOT/name,target_is_directory=True)
print(DEST)
