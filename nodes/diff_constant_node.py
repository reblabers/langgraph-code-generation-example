from .state import GlobalState


class DiffConstantNode:
    async def process(self, global_state: GlobalState) -> GlobalState:
        with open("examples/temp1.diff", "r") as f:
            diff = f.read()

        return {
            **global_state,
            "diff": diff,
        }
