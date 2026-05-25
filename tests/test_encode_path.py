import pytest

from appa_lib.encode_path import encode_path


def test_absolute_path():
    assert encode_path("/Users/karanjot.vendal/dev") == "-Users-karanjot-vendal-dev"


def test_root():
    assert encode_path("/") == "-"


def test_trailing_slash_is_stripped():
    assert encode_path("/Users/x/dev/") == "-Users-x-dev"


def test_dots_in_segments_become_hyphens():
    assert encode_path("/Users/a.b/c.d") == "-Users-a-b-c-d"


def test_rejects_relative_path():
    with pytest.raises(ValueError):
        encode_path("relative/path")
