# -*- coding: utf-8 -*-

import logging
import os.path as path
from os import environ
from coolcantonese.config import Config

level = logging.DEBUG

logging.basicConfig(
    level=level,
    # format='%(message)s',
    format=u'%(levelname)s: %(message)s',
    # format=u'%(levelname)s %(filename)s: %(message)s',
)

cur_dir = path.dirname(path.realpath(__file__))
json_config_filepath = path.join(cur_dir, "config.json")


def test_config():
    default_confing = {
        "ZSH": "",
        "test": 1,
        "env_key": None
    }

    environ["env_key"] = "11"
    config = Config(
        default_confing,
        json_config_filepath=json_config_filepath,
        enable_env_config=True
    )
    assert config.test == "test"
    assert config.env_key == 11
