# -*- coding: utf-8 -*-

# from pprint import pprint as print
import pytest
from coolcantonese.phonetic import (
    NotationMarker,
    fetch_pronunciation,
)


@pytest.fixture
def marker():
    return NotationMarker("coolcantonese/data/phonetic-data.txt")


# def get_notations_result(in_str):
#     return _default.get_notations_result(in_str)


# def get_pronunciations_result(character):
#     return _default.get_pronunciations_result(character)


# def get_characters_result(pronunciation):
#     return _default.get_characters_result(pronunciation)


def test_get_notations_result(marker):
    #  import sys
    #  reload(sys)
    #  sys.setdefaultencoding("utf-8")
    #  print len(_default.char_map)
    in_str = u"屎窟"
    r = marker.get_notations_result(in_str)
    print(r)

    #  print("")
    #  r = get_pronunciations_result(u"中")
    #  print(r)

    #  print
    #  r = get_characters_result("zung1")
    #  print(r)


def test_fetch_pronunciation():
    plist = fetch_pronunciation(u"度")
    for p in plist:
        print(p)
