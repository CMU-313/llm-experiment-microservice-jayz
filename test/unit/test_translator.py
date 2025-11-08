from src.translator import translate_content

from mock import patch
from test.unit import *


def test_chinese():
    is_english, translated_content = translate_content("这是一条中文消息")
    assert is_english == False
    assert translated_content == "This is a Chinese message"

def test_llm_normal_response():
    pass

def test_llm_gibberish_response():
    pass


# Model returns an irrelevant or malformed string
@patch.object(client, 'chat')
def test_unexpected_language(mocker):
    mocker.return_value = {"message": {"content": "I don't understand your request"}}
    result = query_llm_robust("Hier ist dein erstes Beispiel.")
    assert isinstance(result, tuple)
    assert isinstance(result[0], bool)
    assert isinstance(result[1], str)
    # It should not crash, and it should fall back gracefully
    assert result[1] != ""


# Model returns a non-string type (e.g., list or dict)
@patch.object(client, 'chat')
def test_nonstring_language(mocker):
    mocker.return_value = {"message": {"content": ["english"]}}
    result = query_llm_robust("Hello world")
    assert isinstance(result, tuple)
    assert isinstance(result[0], bool)
    assert isinstance(result[1], str)


# Model raises an exception (simulates network or API failure)
@patch.object(client, 'chat', side_effect=Exception("Network down"))
def test_language_api_failure(mocker):
    result = query_llm_robust("Bonjour tout le monde")
    # Should return fallback (True, original_post)
    assert result == (True, "Bonjour tout le monde")


# Model returns empty or whitespace translation
@patch.object(client, 'chat')
def test_empty_translation(mocker):
    # Mock the sequence of calls: first for get_language, then for get_translation
    responses = [
        {"message": {"content": "French"}},   # language
        {"message": {"content": "   "}}       # translation
    ]
    mocker.side_effect = responses
    result = query_llm_robust("Bonjour!")
    # Should fall back to original post if translation is empty
    assert result == (False, "Bonjour!")