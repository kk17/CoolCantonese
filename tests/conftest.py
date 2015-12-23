# -*- coding: utf-8 -*-

import pytest
from coolcantonese.config import Config
from coolcantonese.default_config import default_config
import logging

level = logging.DEBUG

logging.basicConfig(
    level=level,
    # format='%(message)s',
    format=u'%(levelname)s: %(message)s',
    # format=u'%(levelname)s %(filename)s: %(message)s',
)


@pytest.fixture(scope="module")
def config():
    return Config(default_config, None, "~/.coolcantonese.json")
