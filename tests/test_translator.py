# -*- coding: utf-8 -*-

from typing import Any
import pytest
from coolcantonese.translator import (
    SmartTranslator,
    md5,
    TranslateResult,
)
from coolcantonese.config import Config


@pytest.fixture
def ts(config: Config) -> SmartTranslator:
    """Fixture providing a SmartTranslator instance.
    
    Args:
        config: Application configuration fixture
    
    Returns:
        SmartTranslator: Configured translator instance
    """
    return SmartTranslator(config)


def test_md5() -> None:
    """Test MD5 hash generation."""
    text = "2015063000000001apple143566028812345678"
    expected = "f89f9594663708c1605f3d736d01d2d4"
    assert md5(text) == expected, "MD5 hash does not match expected value"


@pytest.mark.parametrize("text", [
    "哋嫲嚟噏咗着攞嗰嘢瞓吖啫攰氹冚",  # Complex Cantonese text
])
def test_individual_translators(ts: SmartTranslator, text: str) -> None:
    """Test translation with each individual translator.
    
    Args:
        ts: SmartTranslator fixture
        text: Text to translate
    """
    for translator in ts.translators:
        result = translator.get_translation(text)
        assert result is not None, f"Translator {translator.__class__.__name__} returned None"
        assert isinstance(result, TranslateResult), f"Translator {translator.__class__.__name__} returned wrong type"
        assert result.words, f"Translator {translator.__class__.__name__} returned empty translation"


@pytest.mark.parametrize("text", [
    "哋嫲嚟噏咗着攞嗰嘢瞓吖啫攰氹冚",  # Complex Cantonese text
])
def test_smart_translator(ts: SmartTranslator, text: str) -> None:
    """Test translation with SmartTranslator.
    
    Args:
        ts: SmartTranslator fixture
        text: Text to translate
    """
    result = ts.get_translation(text)
    assert result is not None, "SmartTranslator returned None"
    assert isinstance(result, TranslateResult), "SmartTranslator returned wrong type"
    assert result.words, "SmartTranslator returned empty translation"
