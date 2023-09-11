import logging
from typing import Any, Dict, List, Union
from urllib.parse import urljoin

import requests
import yaml
from pydantic.v1 import BaseModel, Field, create_model

from .exceptions import ToolNotFoundException
from .model import Endpoint, OpenApiTool
from .utils import convert_to_iso639

TOOL_DIRECTORY_ENDPOINT = 'https://tool-directory.dialogplay.jp'


class ToolLoader:
    def __init__(self, name: str, language='en'):
        integration_url = TOOL_DIRECTORY_ENDPOINT + f'/integrations/{name}/integration.yaml'
        self.integration = self._fetch_integration(integration_url)

        openapi_url = urljoin(integration_url, self.integration.get('openApi'))
        spec = self._fetch_openapi_spec(openapi_url)

        self.spec = self._override(spec, self.integration, language)

    def get_tools(self, parameters: Dict[str, str] = {}) -> List[OpenApiTool]:
        servers = [x.get('url') for x in self.spec.get('servers', [])]

        tools = []
        for endpoint in self._load_endpoints(self.spec):
            tools.append(
                OpenApiTool(
                    description=self.integration.get('description'),
                    server=servers[0],
                    endpoint=endpoint,
                    parameters=parameters,
                )
            )

        return tools

    def _fetch_integration(self, url: str):
        response = requests.get(url)
        if response.status_code == 404:
            raise ToolNotFoundException(f'Specified tool({url}) does not found in tool directory.')

        response.raise_for_status()

        return yaml.load(response.content, Loader=yaml.SafeLoader)

    def _fetch_openapi_spec(self, url: str):
        response = requests.get(url)
        response.raise_for_status()

        return yaml.load(response.content, Loader=yaml.SafeLoader)

    def _override(self, spec: Dict[str, Any], integration: Dict[str, Any], language: str) -> Dict[str, Any]:
        for path, detail in integration.get('paths', {}).items():
            for method, endpoint in detail.items():
                try:
                    if endpoint.get('description'):
                        spec['paths'][path][method]['description'] = self._translate(endpoint['description'], language)
                    for parameter in endpoint.get('parameters', []):
                        if parameter.get('description'):
                            self._override_parameter(
                                spec['paths'][path][method]['parameters'],
                                _in=parameter['in'],
                                name=parameter['name'],
                                description=self._translate(parameter['description'], language),
                            )
                except KeyError:
                    logging.warning('Failed to override OpenAPI spec', exc_info=True)

        return spec

    def _override_parameter(self, parameters: List[Dict[str, Any]], _in: str, name: str, description: str):
        for parameter in parameters:
            if parameter['in'] == _in and parameter['name'] == name:
                parameter['description'] = description

    def _translate(self, description: Union[str, dict[str, str]], language: str) -> str:
        language = convert_to_iso639(language)
        if isinstance(description, str):
            return description
        return description.get(language, description.get('en', ''))

    def _load_endpoints(self, spec: Dict[str, Any]) -> List[Endpoint]:
        endpoints = []
        for path, detail in spec.get('paths', []).items():
            for method, endpoint in detail.items():
                description = endpoint.get('description', endpoint.get('summary', ''))

                endpoints.append(
                    Endpoint(
                        method=method,
                        path=path,
                        description=description,
                        args_schema=self._create_args_schema(endpoint),
                    )
                )

        return endpoints

    def _create_args_schema(self, endpoint: Dict[str, Any]) -> BaseModel:
        # Check required flag and default value
        parameters = {
            x.get('name'): (str, Field()) if x.get('required') else (str, Field(None))
            for x in endpoint.get('parameters', [])
        }

        return create_model('ArgumentsSchema', **parameters)
