import re
import urllib.parse
from functools import cached_property
from typing import Dict, List

import requests
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, computed_field

from .prompt import TOOL_DESCRIPTION


class Endpoint(BaseModel):
    method: str
    path: str
    description: str
    args_schema: type[BaseModel]
    args_source: Dict[str, str]

    @computed_field
    @cached_property
    def path_args(self) -> List[str]:
        return [k for k, v in self.args_source.items() if v == 'path']

    @computed_field
    @cached_property
    def query_args(self) -> List[str]:
        return [k for k, v in self.args_source.items() if v == 'query']

    @computed_field
    @cached_property
    def header_args(self) -> List[str]:
        return [k for k, v in self.args_source.items() if v == 'header']


class OpenApiTool(StructuredTool):
    server: str
    endpoint: Endpoint
    parameters: Dict[str, str]

    def sanitize(self, text):
        text = text.replace('/', '-')
        text = text.replace('.', '-')
        return re.sub(r'[^a-zA-Z0-9_-]', '', text)

    def __init__(self, description: str, server: str, endpoint: Endpoint, parameters: Dict[str, str]):
        url = urllib.parse.urlparse(server)

        name_items = []
        name_items.append(endpoint.method.upper())
        name_items.append(url.netloc)
        if url.path:
            name_items.append(url.path.strip('/'))
        if endpoint.path != '/':
            name_items.append(re.sub(r'\{(.*?)\}', '\\1', endpoint.path.strip('/')))

        tool_description = TOOL_DESCRIPTION.format(
            description=description,
            endpoint=f'{endpoint.method.upper()} {server}{endpoint.path} {endpoint.description}',
        )

        return super().__init__(
            name='-'.join([self.sanitize(x) for x in name_items]),
            description=tool_description,
            server=server,
            endpoint=endpoint,
            args_schema=endpoint.args_schema,
            func=self.request_by_spec,
            parameters=parameters,
        )

    def request_by_spec(self, **kwargs):
        parameters = kwargs | self.parameters
        path_args = {k: v for k, v in parameters.items() if k in self.endpoint.path_args}
        query_args = {k: v for k, v in parameters.items() if k in self.endpoint.query_args}
        header_args = {k: v for k, v in parameters.items() if k in self.endpoint.header_args}
        url = (self.server + self.endpoint.path).format(**path_args)
        if self.endpoint.method == 'get':
            response = requests.get(url, headers=header_args, params=query_args)
        elif self.endpoint.method == 'post':
            response = requests.post(url, headers=header_args, data=query_args)
        else:
            return None

        response.raise_for_status()
        try:
            return response.json()
        except Exception:
            return response.text
