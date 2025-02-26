# -*- coding: utf-8 -*-

from typing import Any
import pytest
from coolcantonese.config import Config
from coolcantonese.default_config import default_config
import logging

level: int = logging.DEBUG

logging.basicConfig(
    level=level,
    # format='%(message)s',
    format=u'%(levelname)s: %(message)s',
    # format=u'%(levelname)s %(filename)s: %(message)s',
)


@pytest.fixture(scope="module")
def config() -> Config:
    """Fixture providing test configuration.
    
    Returns:
        Config: Application configuration for testing
    """
    return Config(default_config, None, "~/.coolcantonese.json")
