from pydantic.v1 import BaseModel

from tool_directory.model import Endpoint, OpenApiTool


def describe_Endpoint():
    class ArgsSchema(BaseModel):
        id: str
        query: str
        authorization: str

    endpoint = Endpoint(
        method='get',
        path='/dummy/{id}',
        description='Endpoint description',
        args_schema=ArgsSchema,
        args_source={'id': 'path', 'api_key': 'query', 'query': 'query', 'authorization': 'header'},
    )

    def describe_path_args():
        def extract_path_args():
            assert endpoint.path_args == ['id']

    def describe_query_args():
        def extract_query_args():
            assert endpoint.query_args == ['api_key', 'query']

    def describe_header_args():
        def extract_header_args():
            assert endpoint.header_args == ['authorization']


def describe_OpenApiTool():
    class ArgsSchema(BaseModel):
        query: str

    class ArgsSchemaWithIdAndHeader(BaseModel):
        id: str
        query: str
        authorization: str

    def describe_init():
        def initialize_tool():
            endpoint = Endpoint(
                method='get',
                path='/dummy',
                description='Endpoint description',
                args_schema=ArgsSchema,
                args_source={'api_key': 'query', 'query': 'query'},
            )
            tool = OpenApiTool(
                description='Integration description',
                server='http://localhost',
                endpoint=endpoint,
                parameters={'api_key': 'dummy'},
            )
            assert tool.name == 'GET http://localhost/dummy'
            assert tool.description == 'Description: Integration description\nEndpoint: GET /dummy Endpoint description'
            assert tool.server == 'http://localhost'
            assert tool.endpoint == endpoint
            assert tool.parameters == {'api_key': 'dummy'}

        def initialize_tool_with_braces():
            endpoint = Endpoint(
                method='get',
                path='/dummy/{id}',
                description='Endpoint description',
                args_schema=ArgsSchemaWithIdAndHeader,
                args_source={'id': 'path', 'api_key': 'query', 'query': 'query'},
            )
            tool = OpenApiTool(
                description='Integration description',
                server='http://localhost',
                endpoint=endpoint,
                parameters={'api_key': 'dummy'},
            )
            assert tool.name == 'GET http://localhost/dummy/:id'
            assert (
                tool.description
                == 'Description: Integration description\nEndpoint: GET /dummy/:id Endpoint description'
            )
            assert tool.server == 'http://localhost'
            assert tool.endpoint == endpoint
            assert tool.parameters == {'api_key': 'dummy'}

    def describe_request_by_spec():
        def send_get_request(requests_mock):
            requests_mock.get('http://localhost/dummy', text='{"result": "dummy"}')

            endpoint = Endpoint(
                method='get',
                path='/dummy',
                description='Endpoint description',
                args_schema=ArgsSchema,
                args_source={'api_key': 'query', 'query': 'query'},
            )
            tool = OpenApiTool(
                description='Integration description',
                server='http://localhost',
                endpoint=endpoint,
                parameters={'api_key': 'dummy'},
            )
            result = tool.request_by_spec(query='dummy query')
            assert result == {'result': 'dummy'}

            assert len(requests_mock.request_history) == 1

            history = requests_mock.request_history[0]
            assert history.method == 'GET'
            assert history.scheme == 'http'
            assert history.netloc == 'localhost'
            assert history.path == '/dummy'
            assert history.qs == {
                'api_key': ['dummy'],
                'query': ['dummy query'],
            }

        def send_get_request_and_return_plain_text(requests_mock):
            requests_mock.get('http://localhost/dummy', text='result is plain text')

            endpoint = Endpoint(
                method='get',
                path='/dummy',
                description='Endpoint description',
                args_schema=ArgsSchema,
                args_source={'query': 'query'},
            )
            tool = OpenApiTool(
                description='Integration description',
                server='http://localhost',
                endpoint=endpoint,
                parameters={},
            )
            result = tool.request_by_spec(query='dummy query')
            assert result == 'result is plain text'

        def send_get_request_with_headers(requests_mock):
            requests_mock.get('http://localhost/dummy', text='result is plain text')

            endpoint = Endpoint(
                method='get',
                path='/dummy',
                description='Endpoint description',
                args_schema=ArgsSchemaWithIdAndHeader,
                args_source={'query': 'query', 'authorization': 'header'},
            )
            tool = OpenApiTool(
                description='Integration description',
                server='http://localhost',
                endpoint=endpoint,
                parameters={'authorization': 'Bearer dummy'},
            )
            result = tool.request_by_spec(query='dummy query')
            assert result == 'result is plain text'

            history = requests_mock.request_history[0]
            assert history.method == 'GET'
            assert history.scheme == 'http'
            assert history.netloc == 'localhost'
            assert history.path == '/dummy'
            assert history.headers.get('authorization') == 'Bearer dummy'
            assert history.qs == {
                'query': ['dummy query'],
            }

        def send_post_request(requests_mock):
            requests_mock.post('http://localhost/dummy', text='{"result": "dummy"}')

            endpoint = Endpoint(
                method='post',
                path='/dummy',
                description='Endpoint description',
                args_schema=ArgsSchema,
                args_source={'api_key': 'query', 'query': 'query'},
            )
            tool = OpenApiTool(
                description='Integration description',
                server='http://localhost',
                endpoint=endpoint,
                parameters={'api_key': 'dummy'},
            )
            result = tool.request_by_spec(query='dummy query')
            assert result == {'result': 'dummy'}

            assert len(requests_mock.request_history) == 1

            history = requests_mock.request_history[0]
            assert history.method == 'POST'
            assert history.scheme == 'http'
            assert history.netloc == 'localhost'
            assert history.path == '/dummy'
            assert history.text == 'query=dummy+query&api_key=dummy'

        def send_request_with_parameter_in_path(requests_mock):
            requests_mock.get('http://localhost/dummy/42', text='{"result": "dummy"}')

            endpoint = Endpoint(
                method='get',
                path='/dummy/{id}',
                description='Endpoint description',
                args_schema=ArgsSchemaWithIdAndHeader,
                args_source={'id': 'path', 'api_key': 'query', 'query': 'query'},
            )
            tool = OpenApiTool(
                description='Integration description',
                server='http://localhost',
                endpoint=endpoint,
                parameters={'api_key': 'dummy'},
            )
            result = tool.request_by_spec(id='42', query='dummy query')
            assert result == {'result': 'dummy'}

            assert len(requests_mock.request_history) == 1

            history = requests_mock.request_history[0]
            assert history.method == 'GET'
            assert history.scheme == 'http'
            assert history.netloc == 'localhost'
            assert history.path == '/dummy/42'
            assert history.qs == {
                'api_key': ['dummy'],
                'query': ['dummy query'],
            }

        def ignore_unsupported_method(requests_mock):
            endpoint = Endpoint(
                method='patch',
                path='/dummy',
                description='Endpoint description',
                args_schema=ArgsSchema,
                args_source={'query': 'query'},
            )
            tool = OpenApiTool(
                description='Integration description',
                server='http://localhost',
                endpoint=endpoint,
                parameters={'api_key': 'dummy'},
            )
            result = tool.request_by_spec(query='dummy query')
            assert result is None

            assert len(requests_mock.request_history) == 0
