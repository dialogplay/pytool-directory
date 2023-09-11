import pytest

from tool_directory import OpenApiTool, ToolLoader
from tool_directory.exceptions import ToolNotFoundException


def describe_ToolLoader():
    def describe_init():
        def load_overridden_spec(requests_mock):
            loader = ToolLoader('sample')
            assert loader.spec['paths']['/pets']['get']['description'] == 'Retrieves dummy data from api.'
            assert loader.spec['paths']['/pets']['post']['description'] == 'Create a pet'

        def load_overridden_spec_with_language(requests_mock):
            loader = ToolLoader('sample', language='ja')
            assert loader.spec['paths']['/pets']['get']['description'] == 'APIからダミーデータを取得する。'
            assert loader.spec['paths']['/pets']['post']['description'] == 'Create a pet'

        def not_found(requests_mock):
            with pytest.raises(ToolNotFoundException) as excinfo:
                ToolLoader('not_found')

            assert (
                str(excinfo.value)
                == 'Specified tool(https://tool-directory.dialogplay.jp/integrations/not_found/integration.yaml) does'
                ' not found in tool directory.'
            )

    def describe_get_tools():
        def return_tools_from_endpoints(requests_mock):
            loader = ToolLoader('sample')
            tools = loader.get_tools(parameters={'api_key': 'dummy'})
            assert len(tools) == 3
            assert isinstance(tools[0], OpenApiTool)

            assert tools[0].name == 'GET http://localhost/dummy/pets'
            assert tools[1].name == 'POST http://localhost/dummy/pets'
            assert tools[2].name == 'GET http://localhost/dummy/pets/:petId'

            assert (
                tools[0].description
                == 'Description: dummy integration description\nEndpoint: GET /pets Retrieves dummy data from api.'
            )
            assert (
                tools[1].description == 'Description: dummy integration description\nEndpoint: POST /pets Create a pet'
            )
            assert (
                tools[2].description
                == 'Description: dummy integration description\nEndpoint: GET /pets/:petId Info for a specific pet'
            )

            assert tools[0].server == 'http://localhost/dummy'
            assert tools[1].server == 'http://localhost/dummy'
            assert tools[2].server == 'http://localhost/dummy'

            assert tools[0].endpoint.method == 'get'
            assert tools[1].endpoint.method == 'post'
            assert tools[2].endpoint.method == 'get'

            assert tools[0].endpoint.path == '/pets'
            assert tools[1].endpoint.path == '/pets'
            assert tools[2].endpoint.path == '/pets/{petId}'

            assert tools[0].endpoint.description == 'Retrieves dummy data from api.'
            assert tools[1].endpoint.description == 'Create a pet'
            assert tools[2].endpoint.description == 'Info for a specific pet'

            assert tools[0].parameters == {'api_key': 'dummy'}
            assert tools[1].parameters == {'api_key': 'dummy'}
            assert tools[2].parameters == {'api_key': 'dummy'}

            assert tools[0].args_schema.schema().get('properties').keys() == {'api_key', 'limit'}
            assert tools[1].args_schema.schema().get('properties').keys() == set()
            assert tools[2].args_schema.schema().get('properties').keys() == {'petId'}

            assert tools[0].args_schema.schema().get('required', []) == ['api_key']
            assert tools[1].args_schema.schema().get('required', []) == []
            assert tools[2].args_schema.schema().get('required', []) == ['petId']
