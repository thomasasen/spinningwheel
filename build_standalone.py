"""Generate the canonical Casino Noir standalone with the maintained Node bundler."""
from pathlib import Path
import subprocess

subprocess.run(["node", str(Path(__file__).parent / "scripts" / "build-standalone.mjs")],
               check=True)
