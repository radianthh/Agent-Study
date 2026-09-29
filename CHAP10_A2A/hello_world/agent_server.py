from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)

import uvicorn
from a2a.server.tasks import InMemoryTaskStore
from agent_executor import HelloWorldAgentExecutor
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.apps import A2AStarletteApplication

def create_agent_card() -> AgentCard:
    """
    에이전트 카드 생성

    AgentCard는 에이전트의 메타데이터를 담고 있으며,
    클라이언트가 에이전트의 기능을 파악할 수 있게 합니다.

    Returns:
        AgentCard: 에이전트 정보 카드
    """

    skill = AgentSkill(
        id='hello_world',
        name='Hello World 인사',
        description='간단한 인사말을 반환합니다',
        tags=['인사', 'hello world', '기본'],
        examples=['안녕', '안녕하세요', 'hi', 'hello'],
    )

    capabilities = AgentCapabilities(
        streaming=False,
        input_modes = ['text'],
        output_modes = ['text'],
    )

    agent_card = AgentCard(
        name='Hello World 에이전트',
        description='A2A 프로토콜을 학습하기 위한 가장 간단한 에이전트입니다',
        url = 'http://localhost:9999',
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=capabilities,
        skills=[skill],
    )

    return agent_card

def main():
    agent_card = create_agent_card()

    agent_executor = HelloWorldAgentExecutor()

    task_store = InMemoryTaskStore()

    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor,
        task_store=task_store,
    )

    server_app = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler = request_handler,
    )

    uvicorn.run(
        server_app.build(),
        host='0.0.0.0',
        port=9999,
    )

if __name__ == '__main__':
    main()