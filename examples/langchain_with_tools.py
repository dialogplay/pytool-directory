import os
import sys

from langchain_openai.chat_models import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from tool_directory import ToolLoader

if 'OPENWEATHER_APP_ID' not in os.environ:
    print('Usage: OPENWEATHER_APP_ID=appid python langchain_with_tools.py')
    print()
    print('Execute with following environment variables.')
    print('    - OPENAI_API_KEY: The API Key for OpenAI')
    print('    - OPENWEATHER_APP_ID: The API Key for OpenWeather')
    sys.exit(1)

# Execute with following environment variables
#   - OPENAI_API_KEY: The API Key for OpenAI
#   - OPENWEATHER_APP_ID: The API Key for OpenWeather
appid = os.environ.get('OPENWEATHER_APP_ID')
llm = ChatOpenAI(temperature=0, model='gpt-4')

tools = ToolLoader('openweather').get_tools(parameters={'appid': appid})

agent = create_react_agent(llm, tools)
messages = agent.invoke({'messages': [('human', 'Please tell me about the temperature in tokyo.')]})
print(messages['messages'][-1].content)
