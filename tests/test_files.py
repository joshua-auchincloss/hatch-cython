from hatch_cython.config.files import FileArgs


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
