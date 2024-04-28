import subprocess
import sys
from glob import glob
from logging import DEBUG, StreamHandler, getLogger

logger = getLogger(__file__)
logger.setLevel(DEBUG)
logger.addHandler(StreamHandler(sys.stdout))

if __name__ == "__main__":
    logger.info(sys.executable)
    logger.info(sys.version_info)
    ext = "whl" if (len(sys.argv) == 1) else sys.argv[1]
    artifact = glob(f"dist/example*.{ext}")[0]
    proc = subprocess.run(  # noqa: PLW1510
        [sys.executable, "-m", "pip", "install", artifact, "--force-reinstall"],  # noqa: S603
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if proc.returncode:
        logger.error(proc.stdout.decode())
        raise SystemExit(1)
