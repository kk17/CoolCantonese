# -*- coding: utf-8 -*-

# from pprint import pprint as print
import pytest
from coolcantonese.phonetic import (
    NotationMarker,
    fetch_symbols,
)


@pytest.fixture
def marker():
    return NotationMarker("coolcantonese/data/phonetic-data.txt")


# def get_noted_chars(in_str):
#     return _default.get_noted_chars(in_str)


# def get_symbols(char):
#     return _default.get_symbols(char)


# def get_chars(symbols):
#     return _default.get_chars(symbols)


def test_get_noted_chars(marker):
    #  import sys
    #  reload(sys)
    #  sys.setdefaultencoding("utf-8")
    #  print len(_default.char_map)
    in_str = u"屎窟"
    r = marker.get_noted_chars(in_str)
    print(r)

    #  print("")
    #  r = get_symbols(u"中")
    #  print(r)

    #  print
    #  r = get_chars("zung1")
    #  print(r)


def test_fetch_symbols():
    noted_chars = fetch_symbols(u"度")
    for p in noted_chars:
        print(p)
