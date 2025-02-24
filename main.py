import asyncio
from graphs.code_generator_graph import build_code_generator_graph, initial_state
from utils.credentials import get_default_credentials
from utils.llm import get_bedrock_llm
from utils.repository import Repository
from pathlib import Path


async def main():
    credentials = get_default_credentials()
    llm = get_bedrock_llm(credentials)

    repository = Repository(Path("repositories/kotlin-tracer-mcp"))
    repository.clean()

    graph = build_code_generator_graph(llm, repository)

    global_state = initial_state(
        source_code_path=Path("repositories/kotlin-tracer-mcp/src/main/kotlin/com/example/Finder.kt"),
        test_code_path=Path("repositories/kotlin-tracer-mcp/src/test/kotlin/com/example/FinderTest.kt"),
    )

    result = await graph.ainvoke(global_state)
    import pprint
    pprint.pprint(result['faults'])


if __name__ == "__main__":
    asyncio.run(main())
