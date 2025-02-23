from state import State

def node_1(state: State) -> State:
    print("---Node 1---")
    return {"graph_state": state['graph_state'] +" I am", "bar": [4]} 