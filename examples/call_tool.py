# Agentを利用せずにToolを呼び出すサンプル

from credentials import get_default_credentials
from facade import get_bedrock_llm
from typing import Annotated
from langchain_core.runnables import chain
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools.apply_to_file import create_mutation_diff
from utils.diff_applier import apply_diff_to_file

credentials = get_default_credentials()
llm = get_bedrock_llm(credentials)

@tool
def add(
    a: Annotated[int, 'first number'],
    b: Annotated[int, 'second number'],
) -> int:
    """Adds a and b."""
    print(f"add: {a} + {b}")
    return a + b


@tool
def multiply(
    a: Annotated[int, 'first number'],
    b: Annotated[int, 'second number'],
) -> int:
    """Multiplies a and b."""
    print(f"multiply: {a} * {b}")
    return a * b

tools = [add, multiply]

tool_map = {tool.name: tool for tool in tools}


@chain
def tool_calls(response):
    return response.tool_calls

@chain
def tool_router(tool_call):
    return tool_map[tool_call["name"]]


llm_with_tools = llm.bind_tools(tools)

prompt_template = ChatPromptTemplate.from_messages(
    [
        ('system', '与えられたinputに従って計算処理を呼び出してください'),
        ("human", "{query}"),
    ]
)

# https://python.langchain.com/v0.2/docs/how_to/tool_runtime/
chain = prompt_template | llm_with_tools | tool_calls | tool_router.map()

query = "What is 3 * 12? Also, what is 11 + 49?"
chain.invoke({'query': query})
