from state import State

def node_3(state: State) -> State:
    print("---Node 3---")
    return {"graph_state": state['graph_state'] +" sad!"} 