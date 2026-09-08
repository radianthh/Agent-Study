from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.tools import create_retriever_tool

from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DB_PATH = str(Path(__file__).parent / "chroma_db")

vectorstore = Chroma(
    persist_directory=DB_PATH,
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"),
    collection_name="korean_pdf",
)

vectorstore.get()
retreiever = vectorstore.as_retriever(search_kwargs={"k": 3})

retriever_tool = create_retriever_tool(
    retriever=retreiever,
    name = "pdf_search",
    description="use this tool to search information from the Korean Spelling Rules PDF document",
)