import os
import re

import pytest
import requests_mock as requests_mock_module


@pytest.fixture
def requests_mock():
    def text_callback(request, context):
        path = 'tests/fixtures' + request.path
        if os.path.isfile(path):
            context.status_code = 200
            return open(path, 'r', encoding='UTF-8').read()
        else:
            context.status_code = 404
            return 'Not found'

    with requests_mock_module.Mocker() as m:
        pattern = re.compile(r'https://tool-directory.dialogplay.jp/.*')
        m.register_uri('GET', pattern, text=text_callback)
        yield m
