from hatch_cython.config.templates import parse_template_kwds

from .utils import arch_platform


def test_templates():
    def test(kwds: dict):
        with arch_platform("x86_64", "darwin"):
            parsed = parse_template_kwds(kwds.copy())
            found = parsed.find(None, "abc/def/templated.pyx.in")
            assert found == kwds.get("templated_mac")
            found = parsed.find(None, "./abc/def/templated.pyx.in")
            assert found == kwds.get("templated_mac")

        with arch_platform("x86_64", "windows"):
            parsed = parse_template_kwds(kwds.copy())
            found = parsed.find(None, "abc/def/templated.pyx.in")
            assert found == kwds.get("templated_win")
            found = parsed.find(None, "./abc/def/templated.pyx.in")
            assert found == kwds.get("templated_win")

    kwds = {
        "index": [
            {"keyword": "global", "matches": "*"},
            {"keyword": "templated_mac", "matches": "templated.*.in", "platforms": ["darwin"]},
            {"keyword": "templated_win", "matches": "templated.*.in", "platforms": ["windows"]},
        ],
        "global": {"supported": ["int"]},
        "templated_mac": {"supported": ["int", "float"]},
        "templated_win": {"supported": ["int", "float", "complex"]},
    }

    test(kwds)
    form2 = {
        "index": [
            {"keyword": "global", "matches": "*"},
            {"keyword": "templated_mac", "matches": "*/templated*", "platforms": ["darwin"]},
            {"keyword": "templated_win", "matches": "*/templated*", "platforms": ["windows"]},
        ],
        "global": {"supported": ["int"]},
        "templated_mac": {"supported": ["int", "float"]},
        "templated_win": {"supported": ["int", "float", "complex"]},
    }
    test(form2)
