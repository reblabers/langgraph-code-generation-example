from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import chain


class SingleToolCaller:
    def __init__(self, llm, tool):
        self.llm = llm
        self.tool = tool

    def tool_calls(self):
        @chain
        def _tool_calls(response):
            return response.tool_calls
        return _tool_calls

    def tool_router(self):
        @chain
        def _tool_router(tool_call):
            if tool_call["name"] == self.tool.name:
                return self.tool
            raise ValueError(f"Unknown tool: {tool_call['name']}")
        return _tool_router.map()

    async def call(
        self,
        prompt_template: ChatPromptTemplate,
        invoke_args: dict,
    ) -> str:
        llm_with_tools = self.llm.bind_tools([self.tool], tool_choice=self.tool.name)
        tool_calls = self.tool_calls()
        tool_router = self.tool_router()

        # https://python.langchain.com/v0.2/docs/how_to/tool_runtime/
        chain = prompt_template | llm_with_tools | tool_calls | tool_router

        # LLMにプロンプトを送信
        response = await chain.ainvoke(invoke_args)

        if 1 < len(response):
            print("warning: response contains multiple contents")

        # Toolの結果を取得
        return response[0].content
