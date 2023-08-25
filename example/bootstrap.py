import subprocess
import sys
from glob import glob
from logging import getLogger

logger = getLogger()

if __name__ == "__main__":
    artifact = glob("dist/example*.whl")[0]
    proc = subprocess.run(  # noqa: PLW1510
        [sys.executable, "-m", "pip", "install", artifact, "--force-reinstall"],  # noqa: S603
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if proc.returncode:
        logger.error(proc.stdout.decode())
        raise SystemExit(1)
