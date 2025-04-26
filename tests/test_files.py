from hatch_cythonize.config.files import FileArgs


def test_file_config():
    cfg = {
        "exclude": [
            "*/abc",
            {"matches": "*/123fg"},
        ],
        "aliases": {},
    }

    fa = FileArgs(**cfg)

    assert sorted([f.matches for f in fa.exclude if f.applies()]) == ["*/123fg", "*/abc"]


def test_fc_with_explicit_targets():
    cfg = {
        "targets": [
            "*/abc.py",
            {"matches": "*/def.py"},
        ],
        "exclude": [],
        "aliases": {},
    }

    fa = FileArgs(**cfg)

    assert fa.explicit_targets


def test_fc_aliasing():
    cfg = {
        "targets": [],
        "exclude": [],
        "aliases": {
            "somelib.abc.next": "somelib.abc.not_first",
            "somelib.abc.alias": "somelib.abc.compiled",
        },
    }

    fa = FileArgs(**cfg)
    assert fa.matches_alias("somelib.abc.alias") == "somelib.abc.compiled"
