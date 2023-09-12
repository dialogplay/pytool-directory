pytool-directory
=========================
Python package to create langchain tool from the [Tool Directory For LangChain](https://github.com/dialogplay/tool-directory/).

Can create langchain tool from definition in the Tool Directory.

Installation
-------------------------
```
pip install pytool-directory
```

Usage
-------------------------
1. Search tools for your destination from [Tool Directory For LangChain](https://github.com/dialogplay/tool-directory).
2. Load tools from the name of integration.
```
from tool_directory import ToolLoader
tools = ToolLoader('openweather').get_tools(parameters={'appid': 'YOUR_APP_ID_FOR_OPENWEATHER'})
```
3. Ask question to LLM with tools.
```
llm = ChatOpenAI(temperature=0, model_name='gpt-4')
agent = initialize_agent(tools, llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
answer = agent('Please tell me about the temperature in tokyo.')
```

Examples
-------------------------
### [langchain_with_tools.py](https://github.com/dialogplay/pytool-directory/blob/main/examples/langchain_with_tools.py)
Use a tool for the OpenWeather API to get the weather information on specified location.

This example execute following conversation via ChatGPT.

```
User: Please tell me about the temperature in tokyo.
Bot: The current temperature in Tokyo is 29.54°C, but it feels like 32.72°C. The minimum and maximum temperatures today are 27.74°C and 30.45°C respectively. The humidity is 64%.
```

Contribution
-------------------------
1. Fork and clone repository.
2. Install development dependencies.
```
pip install '.[dev]'
```

3. Install pre-commit hook for linter and formatter.
```
pre-commit install
```

4. Commit your changes and send pull request.
