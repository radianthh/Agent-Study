from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import TaskState, Part, TextPart
from a2a.utils import new_agent_text_message, new_task
from agent import LangGraphAgent

class LangGraphAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = LangGraphAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        query = context.get_user_input()

        task = context.current_task
        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)

        updater = TaskUpdater(event_queue, task.id, task.context_id)

        session_id = task.context_id

        try:
            async for item in self.agent.stream(query, session_id):
                is_task_complete = item.get('is_task_complete', False)
                require_user_input = item.get('require_user_input', False)
                content = item.get('content', '')

                if not is_task_complete and not require_user_input:
                    await updater.update_status(
                        TaskState.working,
                        new_agent_text_message(
                            content,
                            task.context_id,
                            task.id,
                        ),
                    )
                elif require_user_input:
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
                elif is_task_complete:
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
                )
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
                "작업이 취소되었습니다.",
                task.context_id,
                task.id,
            )
        )