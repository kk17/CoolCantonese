# -*- coding: utf-8 -*-

import logging


def config_logging():
    level = logging.INFO
    logging.basicConfig(
        level=level,
        # format='%(message)s',
        format=u'%(levelname)s: %(message)s',
        # format=u'%(levelname)s %(filename)s: %(message)s',
    )
