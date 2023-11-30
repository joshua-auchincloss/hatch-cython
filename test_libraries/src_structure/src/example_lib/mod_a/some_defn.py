from typing import Optional


class ValueDefn(object):  # noqa: UP004
    def __init__(self, value: Optional[int] = None):
        self.value = value if value else 0

    def set(self, value):  # noqa: A003
        v = self.value
        self.value = value
        if v:
            return True
        return False
