from langchain_core.tools import tool
from typing import Annotated, Optional
import json


@tool
def output_equivalence(
    is_equivalent: Annotated[bool, 'True if the code is equivalent, False otherwise'],
    reason: Annotated[Optional[str], 'If is_equivalent is False, the reason why the code is not equivalent'] = None,
) -> str:
    r"""
    Output the equivalence of the code.
    """
    return json.dumps({"is_equivalent": is_equivalent, "reason": reason})
