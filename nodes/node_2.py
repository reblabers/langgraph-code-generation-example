from state import State

def node_2(state: State) -> State:
    print("---Node 2---")
    return {"graph_state": state['graph_state'] +" happy!"} 