from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

import json
from langchain.messages import ToolMessage

load_dotenv()

tool = TavilySearch(max_results=3)
tools = [tool]

llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools(tools)

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

def chatbot(state: State):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

graph_builder.add_node("chatbot", chatbot)

class BasicToolNode:
    """
        마지막 AIMessage에서 요청된 도구를 실행하는 노드
    """

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("ERROR: 입력에 메세지가 없습니다.")

        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result, ensure_ascii=False),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}

tool_node = BasicToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

def route_tools(state: State):
    """
    마지막 메시지에 도구 호출이 있는 경우, ToolNode로 라우팅하고 그렇지 않으면 END로 라우팅
    """

    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"ERROR: 입력에 메세지가 없습니다. 상태: {state}")

    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END

graph_builder.add_conditional_edges(
    "chatbot",
    route_tools,
    {"tools": "tools", END: END},
)

graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile()

def invoke():
    response = graph.invoke(
        {
            "messages": ["Langgraph가 무엇인가요?"]
        }
    )

    for msg in response["messages"]:
        msg.pretty_print()

async def ainvoke():
    response = await graph.ainvoke(
        {
             "messages": ["Langgraph가 무엇인가요?"]
        }
    )
    for msg in response["messages"]:
        msg.pretty_print()

def stream():
    response = graph.stream(
        {
             "messages": ["Langgraph가 무엇인가요?"]
        }
    )
    for chunk in response:
        for node, state in chunk.items():
            print("---", node, "---")        
            print(state)
            print("="*60)

async def astream():
    response = graph.astream(
        {
             "messages": ["Langgraph가 무엇인가요?"]
        }
    )
    async for chunk in response:
        for node, state in chunk.items():
            print("---", node, "---")        
            print(state)
            print("="*60)

def stream_values():
    response = graph.stream(
        {
             "messages": ["Langgraph가 무엇인가요?"]
        },
        stream_mode="values"
    )
    for chunk in response:
        for state_key, state_value in chunk.items():
            print("--- 현재 상태 ---")
            for msg in state_value:
                print(f"{type(msg).__name__}: {msg.content[:50]}")
            if state_key == "messages":
                state_value[-1].pretty_print()
            print("="*60)

def stream_messages():
    response = graph.stream(
        {
            "messages": ["Langgraph가 무엇인가요?"]
        },
        stream_mode="messages"
    )

    for token, metadata in response:
        print(token.content)
        # print(metadata["langgraph_node"])

if __name__ == "__main__":
    import asyncio
    asyncio.run(astream())