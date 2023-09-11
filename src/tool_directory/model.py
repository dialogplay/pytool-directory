import re
from typing import Dict, Type

from langchain.tools.base import StructuredTool
from pydantic.v1 import BaseModel

from .prompt import TOOL_DESCRIPTION


class Endpoint(BaseModel):
    method: str
    path: str
    description: str
    args_schema: Type[BaseModel]


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
        return {}
