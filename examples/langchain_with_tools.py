import os
import sys

from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI

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
llm = ChatOpenAI(temperature=0, model_name='gpt-4')

tools = ToolLoader('openweather').get_tools(parameters={'appid': appid})

agent = initialize_agent(tools, llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
answer = agent('Please tell me about the temperature in tokyo.')
print(answer.get('output'))
