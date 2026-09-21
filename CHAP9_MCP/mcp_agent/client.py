from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.prompts import load_mcp_prompt
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

from dotenv import load_dotenv

import readline

load_dotenv()

model = ChatOpenAI(model="gpt-4o")

server_params = StdioServerParameters(
    command="python",
    args=["./server.py"],
)

async def run():
   async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()

        tools = await load_mcp_tools(session)

        agent = create_agent(model, tools, checkpointer=InMemorySaver())

        is_first_input = True
        while True:
           user_input = input("질문을 입력하세요: ")

           if user_input.lower() in ["q", "exit", "quit"]:
              break

           if is_first_input:
              prompts = await load_mcp_prompt(
                 session, "default_prompt", arguments={"message": user_input}
              )
              is_first_input = False

           else:
              prompts = [{"role": "user", "content": user_input}]  

           response = await agent.ainvoke(
              {
                 "messages": prompts
              },
              config = {"configurable": {"user_id": "user_123", "thread_id": "1"}}
           )

           for msg in response["messages"]:
              msg.pretty_print()


import asyncio
asyncio.run(run())