import asyncio
from uuid import uuid4
import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    Message,
    MessageSendParams,
    SendMessageRequest,
    TextPart,
)

async def main():
    agent_url = 'http://localhost:9999'

    async with httpx.AsyncClient() as httpx_client:
        card_resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=agent_url,
        )
        agent_card = await card_resolver.get_agent_card()


        print(f"\n에이전트 정보:")
        print(f"    - 이름: {agent_card.name}")
        print(f"    - 설명: {agent_card.description}")
        print(f"    - 버전: {agent_card.version}")
        print(f"    - 스킬 개수: {len(agent_card.skills)}")

        if agent_card.skills:
            print(f"\n 스킬 목록:")
            for skill in agent_card.skills:
                print(f"   • {skill.name}: {skill.description}")
                if skill.examples:
                    print(f"     예시: {', '.join(skill.examples[:3])}")

        client = A2AClient(
            httpx_client=httpx_client,
            agent_card=agent_card,
        )

        test_messages = [
            "안녕하세요!",
            "Hello",
            "무엇을 할 수 있나요?",
        ]

        for i, user_input in enumerate(test_messages, 1):
            print(f"\n[메시지 {i}/{len(test_messages)}]")
            print(f"👤 사용자: {user_input}")

            message = Message(
                role='user',
                parts=[TextPart(kind='text', text=user_input)],
                message_id=uuid4().hex,
            )

            request = SendMessageRequest(
                id=uuid4().hex,
                params=MessageSendParams(message=message),
            )

            response = await client.send_message(request)

            if hasattr(response, 'root') and response.root:
                result = response.root.result

                if hasattr(result, 'parts') and result.parts:
                    for part in result.parts:
                        if hasattr(part, 'root'):
                            text_part = part.root
                            if hasattr(text_part, 'text'):
                                print(f"🤖 에이전트: {text_part.text}")
            
            if i < len(test_messages):
                await asyncio.sleep(0.5)

if __name__ == '__main__':
    asyncio.run(main())

