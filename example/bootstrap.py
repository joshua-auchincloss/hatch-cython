import subprocess
import sys
from os import name

py310 = (3, 10)
py311 = (3, 11)
py312 = (3, 12)

vmaj = (sys.version_info[0], sys.version_info[1])
cp = "cp310" if vmaj >= py310 and vmaj <= py311 else "cp311" if vmaj >= py311 and vmaj <= py312 else "cp312"

if __name__ == "__main__":
    win = f"dist\\example-0.0.1-{cp}-{cp}-win_amd64.whl"
    posix = "dist/example-*.whl"
    subprocess.run(  # noqa: PLW1510
        [sys.executable, "-m", "pip", "install", win if name == "nt" else posix, "--force-reinstall"],  # noqa: S603
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
