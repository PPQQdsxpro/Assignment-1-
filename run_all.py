"""Run analysis and independent checks from any working directory."""
from pathlib import Path
import subprocess
import sys
root=Path(__file__).resolve().parent
for name in ['segment.py','collocates.py','verify.py','make_report.py','build_materials.py']:
    subprocess.run([sys.executable,str(root/name)],cwd=root,check=True)
