import asyncio
import json
from graphs.code_generator_graph import build_code_generator_graph, initial_state
from utils.credentials import get_default_credentials
from utils.llm import get_bedrock_llm
from utils.repository import Repository
from pathlib import Path
from typing import TypedDict, List, Optional

class Record(TypedDict):
    source_code_path: str
    diff: str
    is_equivalent: bool
    reason: Optional[str] = None


async def main():
    credentials = get_default_credentials()
    llm = get_bedrock_llm(credentials)

    repository = Repository(Path("repositories/kotlin-tracer-mcp"))
    repository.clean()

    graph = build_code_generator_graph(llm, repository)
    
    source_code_path = Path("repositories/kotlin-tracer-mcp/src/main/kotlin/com/example/Finder.kt")
    test_code_path = Path("repositories/kotlin-tracer-mcp/src/test/kotlin/com/example/FinderTest.kt")

    global_state = initial_state(
        source_code_path=source_code_path,
        test_code_path=test_code_path,
    )

    result = await graph.ainvoke(global_state)

    # import pprint
    # pprint.pprint(result)

    # 結果をファイルに保存
    records = []
    for fault in result['faults']:
        records.append(Record(
            source_code_path=str(source_code_path),
            diff=fault['diff'],
            is_equivalent=fault['is_equivalent'],
            reason=fault['reason'],
        ))

    with open("results/last.json", "w") as f:
        json.dump(records, f, indent=4)


if __name__ == "__main__":
    asyncio.run(main())
