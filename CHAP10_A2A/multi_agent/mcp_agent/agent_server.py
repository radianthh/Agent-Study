import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from agent_executor import MCPAgentExecutor

def create_agent_card() -> AgentCard:
    skill = AgentSkill(
        id='mcp_tavily_search',
        name='Tavily 웹 검색 에이전트',
        description='Tavily MCP 서버를 통해 웹 검색을 수행하고 최신 정보를 제공합니다',
        tags=['mcp', 'tavily', 'web search', 'internet'],
        examples=['파이썬 최신 트렌드 알려줘', 'AI 에이전트란?', '2025년 기술 동향 검색해줘'],
    )

    capabilities = AgentCapabilities(
        streaming=True,
        input_modes=['text'],
        output_modes=['text'],
    )

    agent_card = AgentCard(
        name='Tavily MCP Search Agent',
        description='Tavily MCP 서버를 사용하여 웹 검색을 수행하는 에이전트입니다. LangGraph와 LangChain을 사용하지 않고 순수 MCP 프로토콜로 구현되었습니다.',
        url='http://localhost:10002',
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=capabilities,
        skills=[skill],
    )

    return agent_card

def main():
    agent_card = create_agent_card()
    agent_executor = MCPAgentExecutor()
    task_store = InMemoryTaskStore()

    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor,
        task_store=task_store,
    )

    server_app = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

    uvicorn.run(
        server_app.build(),
        host='0.0.0.0',
        port=10002,
    )

if __name__ == '__main__':
    main()