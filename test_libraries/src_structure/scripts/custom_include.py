import json
from pathlib import Path

CALLED_INCLUDES = False
CALLED_MUST = False


def update():
    with open("caller_outputs.json", "w") as f:
        f.write(
            json.dumps(
                {
                    "call": CALLED_MUST,
                    "includes": CALLED_INCLUDES,
                }
            )
        )


def must_call():
    global CALLED_MUST  # noqa: PLW0603
    CALLED_MUST = True
    update()


def gets_includes():
    global CALLED_INCLUDES  # noqa: PLW0603
    CALLED_INCLUDES = True
    update()
    return [str(Path(__file__).parent.parent / "include")]
