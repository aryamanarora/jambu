import subprocess
from pathlib import Path
B=Path('/Users/aryamanarora/Documents/Code/jambu-all/tmp/telugu-metathesis')
pop='/Users/aryamanarora/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdftoppm'
for name,nums in [('garrett-blevins-2009',[12]),('hume-2002',[38]),('winfield-1928',[88,89,90,91,92])]:
 for n in nums:
  subprocess.run([pop,'-f',str(n),'-l',str(n),'-r','140','-png','-singlefile',str(B/(name+'.pdf')),str(B/f'{name}-morph-{n:03}')],check=True)
