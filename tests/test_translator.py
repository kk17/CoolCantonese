# -*- coding: utf-8 -*-

import pytest
from coolcantonese.translator import (
    SmartTranslator,
    md5,
)


@pytest.fixture
def ts(config):
    return SmartTranslator(config)


def test_md5():
    text = "2015063000000001apple143566028812345678"
    result = "f89f9594663708c1605f3d736d01d2d4"
    assert md5(text) == result


def test_get_translation(ts):
    for translator in ts.translators:
        text = u"哋嫲嚟噏咗着攞嗰嘢瞓吖啫攰氹冚"
        result = translator.get_translation(text)
        print(result)


def test_get_translation2(ts):
    text = u"哋嫲嚟噏咗着攞嗰嘢瞓吖啫攰氹冚"
    result = ts.get_translation(text)
    print(result)
