
import logging
import os.path as path
import json
from codecs import open
from os import environ
import six

logger = logging.getLogger(__name__)


def update_config_with_json_config_file(config, config_filepath=None,
                                        global_config_filepath=None):

    if global_config_filepath:
        global_config_filepath = path.expanduser(global_config_filepath)
        if path.exists(global_config_filepath):
            with open(global_config_filepath, "r", "utf-8") as config_file:
                global_config = json.load(config_file, object_hook=dict)
                logger.debug("global json config: %s", global_config)
            config.update(global_config)
    if not config_filepath:
        pass
    elif not path.exists(config_filepath):
        logger.debug("local json config: %s not found.", config_filepath)
    else:
        with open(config_filepath, "r", "utf-8") as config_file:
            json_config = json.load(config_file, object_hook=dict)
        logger.debug("json config: %s.", json_config)
        config.update(json_config)
    return config


def update_config_with_env_config(config):
    env_json_lines = []
    for k, v in config.items():
        if k in environ:
            env_val = environ[k]
            if isinstance(v, six.string_types):
                if not env_val.startswith("\""):
                    env_val = "\"%s\"" % env_val
            env_json_lines.append("\t\"%s\": %s" % (k, env_val))
    json_str = ",\n".join(env_json_lines)
    json_str = "{\n%s\n}" % json_str
    env_config = json.loads(json_str, object_hook=dict)
    logger.debug("env config config: %s.", env_config)
    config.update(env_config)
    return config


class AttrDict(dict):
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        del self[name]


class Config(AttrDict):
    """docstring for Config"""

    def __init__(
            self, default_config_dict=None, json_config_filepath=None,
            global_json_config_filepath=None, enable_env_config=False):

        logger.debug("default config: %s.", default_config_dict or {})
        super(Config, self).__init__(default_config_dict)
        update_config_with_json_config_file(
            self, json_config_filepath, global_json_config_filepath)
        if enable_env_config:
            update_config_with_env_config(self)
        logger.debug("final config: %s.", self)
