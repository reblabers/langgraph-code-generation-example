from langchain_core.tools import tool
from typing import Annotated


@tool
def output_diff(
    diff: Annotated[str, 'unified diff format string. This should not be empty.'],
) -> str:
    r"""
    Output the mutated code in Unified DIFF format.

    Diff Format Example:
    --- original.kt
    +++ mutated.kt
    @@ -1,7 +1,6 @@
    -The Way that can be told of is not the eternal Way;
    -The name that can be named is not the eternal name.
    The Nameless is the origin of Heaven and Earth;
    -The Named is the mother of all things.
    +The named is the mother of all things.
    +
    Therefore let there always be non-being,
    so we may see their subtlety,
    And let there always be being,
    @@ -9,3 +8,6 @@
    The two are the same,
    But after they are produced,
    they have different names.
    +They both may be called deep and profound.
    +Deeper and more profound,
    +The door of all subtleties!
    """
    return diff
