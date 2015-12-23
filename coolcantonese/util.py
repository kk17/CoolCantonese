# -*- coding: utf-8 -*-

import six
from six.moves import urllib


def to_string_type(text):
    if six.PY2 and isinstance(text, six.text_type):
        return text.encode("utf-8")
    return text


def to_text_type(text):
    if not isinstance(text, six.text_type):
        return text.decode("utf-8")
    return text


def pathname2url(path):
    path = to_string_type(path)
    return to_text_type(urllib.request.pathname2url(path))
