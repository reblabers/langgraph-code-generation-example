import asyncio
import json
from graphs.fault_generator_graph import build_fault_generator_graph, initial_state
from utils.credentials import get_default_credentials
from utils.llm import get_bedrock_llm
from utils.repository import Repository
from pathlib import Path
from typing import TypedDict, List, Optional
from nodes.state import Fault


class FaultRecord(TypedDict):
    source_code_path: str
    diff: str
    is_equivalent: bool
    reason: Optional[str] = None


async def main():
    credentials = get_default_credentials()
    llm = get_bedrock_llm(credentials)

    repository = Repository(Path("repositories/kotlin-math-utils"))
    repository.clean()

    graph = build_fault_generator_graph(llm, repository)
    
    source_code_path = Path("repositories/kotlin-math-utils/src/main/kotlin/com/example/math/StatisticsCalculator.kt")
    test_code_path = Path("repositories/kotlin-math-utils/src/test/kotlin/com/example/math/StatisticsCalculatorTest.kt")

    global_state = initial_state(
        source_code_path=source_code_path,
        test_code_path=test_code_path,
    )

    result = await graph.ainvoke(global_state)

    print("COMPLETED")

    # 結果をファイルに保存
    records = []
    for fault in result['faults']:
        diff = fault['diff']
        is_equivalent = fault['is_equivalent']
        reason = fault['reason']    

        records.append(FaultRecord(
            source_code_path=str(source_code_path),
            diff=diff,
            is_equivalent=is_equivalent,
            reason=reason,
        ))

        # デバッグ用に結果を表示
        print("###")
        print("source_code_path:", source_code_path)
        print("is_equivalent:", is_equivalent)
        print("diff:")
        print(diff)
        print("reason:")
        print(reason)

    with open("results/last_faults.json", "w") as f:
        json.dump(records, f, indent=4)
    
    print("SAVED")


if __name__ == "__main__":
    asyncio.run(main())
