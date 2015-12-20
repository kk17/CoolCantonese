#!/usr/bin/env python
# -*- coding: utf-8 -*-

from coolcantonese.ekho import Ekho
from webtest import TestApp as App
from six.moves import urllib
# import sh
import pytest


# def mock_ekho(*args):
#     if "-l" in args:
#         return "nei5 hou2"
#     elif "-o" in args:
#         filepath = args[5]
#         print(args)
#         sh.touch(filepath)
#     else:
#         raise


# sh.ekho = mock_ekho


@pytest.fixture
def app(tmpdir):
    return App(Ekho(tmpdir.strpath).wsgi)


def test_export_pronounces_audio_ok(app):
    url = urllib.request.pathname2url("/Cantonese/text/你好.mp3")
    result = app.get(url)
    assert result.status_int == 200
    assert result.headers['Content-Type'] == 'audio/mpeg'


def test_get_phonetic_audio_ok(app):
    url = urllib.request.pathname2url("/Cantonese/phonetic/nei5_hou2.wav")
    result = app.get(url)
    assert result.status_int == 200
    assert result.headers['Content-Type'] == 'audio/wav'


def test_get_phonetic_text_ok(app):
    url = urllib.request.pathname2url("/Cantonese/phonetic/你好")
    result = app.get(url)
    assert result.status_int == 200
    assert result.text == "nei5 hou2"


def test_404(app):
    url = urllib.request.pathname2url("/Cantonese/text/你好.kk")
    result = app.get(url, expect_errors=True)
    assert result.status_int == 404
