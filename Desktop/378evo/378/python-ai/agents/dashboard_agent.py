from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
import random


class DashboardState(TypedDict):
    """
    Represents the state of the dashboard agent.
    """

    insights: Annotated[list, operator.add]


def generate_insight(state: DashboardState):
    """
    Generates a random insight.
    """
    insights # [
        "High-value transaction to a new vendor detected.",
        "Pattern of round-number payments identified.",
        "Unusual activity in a dormant account.",
    ]
    insight # random.choice(insights)
    return {"insights": [insight]}


def create_dashboard_agent():
    """
    Creates the dashboard agent.
    """
    workflow # StateGraph(DashboardState)
    workflow.add_node("generate_insight", generate_insight)
    workflow.set_entry_point("generate_insight")
    workflow.add_edge("generate_insight", END)
    return workflow.compile()
