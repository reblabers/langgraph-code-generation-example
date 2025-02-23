import asyncio
from graph_builder import create_graph
from state import State

async def main():
    graph = create_graph()
    val = graph.get_graph().draw_mermaid_png()
    
    # バイナリモードでファイルを開いて書き込み
    with open("graph.png", "wb") as f:
        f.write(val)
    
    result = graph.invoke({"graph_state" : "Hi, this is Lance.", "bar" : [1, 2, 3]})
    print(result)

if __name__ == "__main__":
    asyncio.run(main()) 