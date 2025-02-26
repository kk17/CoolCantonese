# -*- coding: utf-8 -*-

from typing import Dict, Any
import logging
import os.path as path
from os import environ
import pytest
from coolcantonese.config import Config

level: int = logging.DEBUG

logging.basicConfig(
    level=level,
    # format='%(message)s',
    format=u'%(levelname)s: %(message)s',
    # format=u'%(levelname)s %(filename)s: %(message)s',
)

cur_dir: str = path.dirname(path.realpath(__file__))
json_config_filepath: str = path.join(cur_dir, "config.json")


@pytest.fixture
def default_config_dict() -> Dict[str, Any]:
    """Fixture providing default test configuration.
    
    Returns:
        Dict[str, Any]: Default configuration dictionary
    """
    return {
        "ZSH": "",
        "test": 1,
        "env_key": None
    }


def test_config(default_config_dict: Dict[str, Any]) -> None:
    """Test configuration loading from different sources.
    
    Tests that configuration values are correctly loaded from:
    - Default configuration
    - JSON file
    - Environment variables
    
    Args:
        default_config_dict: Default configuration fixture
    """
    # Set up environment variable
    environ["env_key"] = "11"
    
    # Create config instance
    config = Config(
        default_config_dict,
        json_config_filepath=json_config_filepath,
        enable_env_config=True
    )
    
    # Test configuration values
    assert config.test == "test", "JSON config value not loaded correctly"
    assert config.env_key == 11, "Environment variable not loaded correctly"
    
    # Clean up
    del environ["env_key"]
