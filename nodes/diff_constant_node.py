from .state import GlobalState


class DiffConstantNode:
    async def process(self, global_state: GlobalState) -> GlobalState:
        with open("debug/last_diff_generator.diff", "r") as f:
            diff = f.read()

        return {
            **global_state,
            "diff": diff,
        }
