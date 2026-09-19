from typing import List
from langgraph.graph import MessagesState

from langchain_openai import ChatOpenAI

class State(MessagesState):
    plan: List[str]
    past_steps: List[tuple]

class SupervisorState(MessagesState):
    plan: List[str]
    next: str
    past_steps: List[tuple]

def get_model():
    llm = ChatOpenAI(model="gpt-4o-mini")
    return llm