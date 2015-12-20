# -*- coding: utf-8 -*-

import pytest
from coolcantonese.tuling import TulingService


@pytest.fixture
def tuling(config):
    return TulingService(config.tuling_api_key)


def test_tuling(tuling):
    ret, msg = tuling.send_msg("kk17", "你好吗")
    print(msg)
