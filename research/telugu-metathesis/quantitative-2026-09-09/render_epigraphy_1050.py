import subprocess
from pathlib import Path
base=Path('/Users/aryamanarora/Documents/Code/jambu-all/tmp/telugu-metathesis')
pop='/Users/aryamanarora/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdftoppm'
for n in [312,321]:
    subprocess.run([pop,'-f',str(n),'-l',str(n),'-r','130','-png','-singlefile',str(base/'sastri1969.pdf'),str(base/f'sastri1969-pypdf-page-{n:03}')],check=True)
