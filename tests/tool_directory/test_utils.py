import pytest

from tool_directory.utils import convert_to_iso639


@pytest.mark.parametrize(
    'language, expected',
    [
        ('', ''),
        ('ja', 'ja'),
        ('ja-jp', 'ja'),
        ('ja_JP', 'ja'),
    ],
)
def test_convert_to_iso639(language, expected):
    assert convert_to_iso639(language) == expected
