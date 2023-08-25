import subprocess
import sys
from glob import glob
from logging import getLogger

logger = getLogger()

py310 = (3, 10)
py311 = (3, 11)
py312 = (3, 12)

vmaj = (sys.version_info[0], sys.version_info[1])
cp = "cp310" if vmaj >= py310 and vmaj <= py311 else "cp311" if vmaj >= py311 and vmaj <= py312 else "cp312"

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
