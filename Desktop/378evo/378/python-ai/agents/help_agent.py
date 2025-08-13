from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


class HelpState(TypedDict):
    """
    Represents the state of the help agent.
    """

    user_context: dict
    retrieved_documents: list
    suggestion: str


def retrieve_documents(state: HelpState):
    """
    Retrieves documents from the vector store based on the user context.
    """
    vectorstore = Chroma(
        persist_directory="./chroma_db", embedding_function=OpenAIEmbeddings()
    )
    retriever = vectorstore.as_retriever()
    documents = retriever.get_relevant_documents(state["user_context"]["page"])
    return {"retrieved_documents": documents}


def generate_suggestion(state: HelpState):
    """
    Generates a suggestion based on the retrieved documents.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant. Your task is to provide a suggestion to the user based on the following documents:\n\n{documents}",
            ),
            ("user", "{user_context}"),
        ]
    )
    llm = ChatOpenAI(model_name="gpt-4", temperature=0)
    chain = prompt | llm
    suggestion = chain.invoke(
        {
            "documents": state["retrieved_documents"],
            "user_context": state["user_context"],
        }
    )
    return {"suggestion": suggestion.content}


def create_help_agent():
    """
    Creates the help agent.
    """
    workflow = StateGraph(HelpState)
    workflow.add_node("retrieve_documents", retrieve_documents)
    workflow.add_node("generate_suggestion", generate_suggestion)
    workflow.set_entry_point("retrieve_documents")
    workflow.add_edge("retrieve_documents", "generate_suggestion")
    workflow.add_edge("generate_suggestion", END)
    return workflow.compile()
