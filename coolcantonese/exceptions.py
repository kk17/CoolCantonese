# -*- coding: utf-8 -*-

"""
coolcantonese.exceptions
-----------------------

All exceptions used in the CoolCantonese code base are defined here.
"""


class CoolCantoneseException(Exception):
    """
    Base exception class. All CoolCantonese-specific exceptions should subclass
    this class.

    """


class TranslationException(CoolCantoneseException):
    pass
