import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

from typing import Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.types import Command
from langchain_core.messages import HumanMessage, AIMessage

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

import asyncio

load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


model = ChatOpenAI(model="gpt-4o-mini")

class Router(TypedDict):
    """라우팅할 작업자
    file_searcher: 파일 정보 호출 및 생성 작업자
    web_searcher: 웹 검색 작업자
    """
    next: Literal["file_searcher", "web_searcher"]

class State(MessagesState):
    next: str

async def run():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    client = MultiServerMCPClient(
        {
            "tavily": {
                "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}",
                "transport": "streamable_http",
            },
            "file": {
                "transport": "stdio",
                "command": "python",
                "args": ["./server.py"],
            }
        }
    )

    all_tools = await client.get_tools()
    print(f"Total tools loaded: {len(all_tools)}")
    print(f"Tool names: {[tool.name for tool in all_tools]}")

    tavily_tools = await client.get_tools(server_name="tavily")
    file_tools = await client.get_tools(server_name="file")
    print(f"Tavily tools: {[tool.name for tool in tavily_tools]}")
    print(f"File tools: {[tool.name for tool in file_tools]}")

    members = ["file_searcher", "web_searcher"]

    system_prompt = f"""
당신은 다음 작업자들 간의 대화를 관리하는 슈퍼바이저입니다.
작업자들은 다음과 같습니다: {members}
특정 작업자가 수행할 작업이 있다면 Router 도구를 사용해 다음 작업자를 지정하세요.
작업이 필요 없거나 즉시 답변하고, 이미 작업을 완료했다면 최종 답변을 반환하세요.
"""

    async def supervisor_node(
            state: State,
    ) -> Command[Literal["file_searcher", "web_searcher", END]]:
        messages = [
            {"role": "system", "content": system_prompt},
        ] + state["messages"]

        response = await model.bind_tools([Router]).ainvoke(messages)

        if hasattr(response, "tool_calls") and len(response.tool_calls) > 0:
            goto = response.tool_calls[0]["args"]["next"]
            return Command(goto=goto, update={"next": goto})

        else:
            final_message = AIMessage(content=response.content, name="supervisor")
            return Command(
                goto=END,
                update={"messages": [final_message]},
            )

    file_searcher = create_agent(model, file_tools)

    async def file_search_node(state: State) -> Command[Literal["supervisor"]]:
        result = await file_searcher.ainvoke(state)
        return Command(
            update={
                "messages": [
                    HumanMessage(
                        content=result["messages"][-1].content, name="file_searcher"
                    )
                ]
            },
            goto="supervisor",
        )

    web_searcher = create_agent(model, tavily_tools)

    async def web_search_node(state: State) -> Command[Literal["supervisor"]]:
        result = await web_searcher.ainvoke(state)
        return Command(
            update={
                "messages": [
                    HumanMessage(
                        content=result["messages"][-1].content, name="web_searcher"
                    )
                ]
            },
            goto="supervisor",
        )

    graph_builder = StateGraph(State)
    graph_builder.add_edge(START, "supervisor")
    graph_builder.add_node("supervisor", supervisor_node)
    graph_builder.add_node("file_searcher", file_search_node)
    graph_builder.add_node("web_searcher", web_search_node)
    memory = InMemorySaver()
    graph = graph_builder.compile(checkpointer=memory)

    config = {"configurable": {"thread_id": "1"}}
    while True:
        try:
            user_input = input("질문을 입력하세요: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("안녕히 가세요!")
                break

            async for _, chunk in graph.astream(
                {"messages": user_input},
                stream_mode="updates",
                subgraphs=True,
                config=config,
            ):
                for _, node_chunk in chunk.items():
                    if "messages" in node_chunk:
                        node_chunk["messages"][-1].pretty_print()
                    else:
                        print(node_chunk)
        except Exception as e:
            print(f"종료합니다.{e}")
            break

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback

        traceback.print_exc()