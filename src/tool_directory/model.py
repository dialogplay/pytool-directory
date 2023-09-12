import re
from functools import cached_property
from typing import Dict, Type

import requests
from langchain.tools.base import StructuredTool
from pydantic.v1 import BaseModel

from .prompt import TOOL_DESCRIPTION


class Endpoint(BaseModel):
    method: str
    path: str
    description: str
    args_schema: Type[BaseModel]
    args_source: Dict[str, str]

    class Config:
        # Allow @cached_property with pydantic v1
        keep_untouched = (cached_property,)

    @cached_property
    def path_args(self):
        return [k for k, v in self.args_source.items() if v == 'path']

    @cached_property
    def query_args(self):
        return [k for k, v in self.args_source.items() if v == 'query']


class OpenApiTool(StructuredTool):
    server: str
    endpoint: Endpoint
    parameters: Dict[str, str]

    def __init__(self, description: str, server: str, endpoint: Endpoint, parameters: Dict[str, str]):
        escaped_path = re.sub(r'\{(.*?)\}', ':\\1', endpoint.path)
        tool_description = TOOL_DESCRIPTION.format(
            description=description, endpoint=f'{endpoint.method.upper()} {escaped_path} {endpoint.description}'
        )

        return super().__init__(
            name=f'{endpoint.method.upper()} {server}{escaped_path}',
            description=tool_description,
            server=server,
            endpoint=endpoint,
            args_schema=endpoint.args_schema,
            func=self.request_by_spec,
            parameters=parameters,
        )

    def request_by_spec(self, **kwargs):
        path_args = {k: v for k, v in kwargs.items() if k in self.endpoint.path_args}
        query_args = {k: v for k, v in kwargs.items() if k in self.endpoint.query_args}
        url = (self.server + self.endpoint.path).format(**path_args)
        if self.endpoint.method == 'get':
            response = requests.get(url, params=query_args | self.parameters)
        elif self.endpoint.method == 'post':
            response = requests.post(url, data=query_args | self.parameters)

        response.raise_for_status()
        try:
            return response.json()
        except Exception:
            return response.text
