from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import TaskState, Part, TextPart
from a2a.utils import new_agent_text_message, new_task
from agent import MCPAgent

class MCPAgentExecutor(AgentExecutor):
    """
    MCP 에이전트 실행자

    A2A 프로토콜에 맞춰 MCP 에이전트를 실행합니다.
    """

    def __init__(self):
        """에이전트 인스턴스 초기화"""
        self.agent = MCPAgent()
        self.initialized = False

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """
        에이전트를 실행하고 결과를 이벤트 큐에 전송

        Args:
            context: 요청 컨텍스트(사용자 메시지, 세션 정보 등)
            event_queue: 결과를 전송할 이벤트 큐
        """

        if not self.initialized:
            try:
                await self.agent.initialize()
                self.initialized = True
            except Exception as e:
                print(f"MCP 에이전트 초기화 실패: {e}")

        query = context.get_user_input()

        task = context.current_task

        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)

        updater = TaskUpdater(event_queue, task.id, task.context_id)

        try:
            async for item in self.agent.stream(query):
                is_complete = item.get('is_task_complete', False)
                require_input = item.get('require_user_input', False)
                content = item.get('content', '')

                if not is_complete and not require_input and content:
                    await updater.update_status(
                        TaskState.working,
                        new_agent_text_message(
                            content,
                            task.context_id,
                            task.id,
                        )
                    )
                elif require_input:
                    await updater.update_status(
                        TaskState.input_required,
                        new_agent_text_message(
                            content,
                            task.context_id,
                            task.id,
                        ),
                        final=True,
                    )
                    break
                elif is_complete:
                    await updater.add_artifact(
                        parts=[Part(root=TextPart(text=content))],
                        name='agent_result'
                    )
                    await updater.complete()
                    break
        except Exception as e:
            await updater.update_status(
                TaskState.failed,
                new_agent_text_message(
                    f"에러 발생: {str(e)}",
                    task.context_id,
                    task.id,
                ),
            )

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        task = context.current_task

        updater = TaskUpdater(event_queue, task.id, task.context_id)
        await updater.cancel(
            new_agent_text_message(
                "MCP 에이전트 작업이 취소되었습니다.",
                task.context_id,
                task.id,
            )
        )