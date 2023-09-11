import re


def convert_to_iso639(language: str):
    return re.sub(r'[-_].*', '', language)
