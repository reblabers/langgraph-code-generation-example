from .state import GlobalState


class DiffConstantNode:
    async def process(self, global_state: GlobalState) -> GlobalState:
        # file_path = "debug/last_diff_generator.diff""
        file_path = "debug/last_test_generator.diff"
        with open(file_path, "r") as f:
            diff = f.read()

        return {
            **global_state,
            "diff": diff,
        }
