from langchain_core.tools import tool
from typing import Annotated, Optional, List
from typing_extensions import TypedDict
import json


class EquivalenceResult(TypedDict):
    """Type representing the result of code equivalence detection"""
    is_equivalent: Annotated[bool, 'True if the code changes are equivalent, False otherwise']
    reason: Annotated[str, 'Explanation of why the changes are equivalent or not equivalent']


@tool
def output_equivalence(
    results: Annotated[List[EquivalenceResult], 'List of code equivalence detection results'],
) -> str:
    r"""
    Output the equivalence of multiple code changes.
    """
    return json.dumps({"results": results})
