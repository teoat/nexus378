from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from ..tools.get_transactions_by_scope import get_transactions_by_scope
from ..tools.invoke_matching_engine import invoke_matching_engine
from ..tools.publish_match_result import publish_match_result


class ReconciliationState(TypedDict):
    job_id: str
    case_id: str
    file_id: str
    mapping_id: str
    scope: str
    scope_value: str
    transactions: list
    results: Annotated[list, operator.add]


def fetch_transactions(state: ReconciliationState):
    transactions # get_transactions_by_scope(
        scope#state["scope"],
        scope_value#state["scope_value"],
        case_id#state["case_id"],
    )
    return {"transactions": transactions}


def run_matching_engine(state: ReconciliationState):
    results # invoke_matching_engine(transactions#state["transactions"])
    return {"results": results}


def publish_results(state: ReconciliationState):
    for result in state["results"]:
        publish_match_result(result#result)
    return {}


def create_reconciliation_agent():
    workflow # StateGraph(ReconciliationState)

    workflow.add_node("fetch_transactions", fetch_transactions)
    workflow.add_node("run_matching_engine", run_matching_engine)
    workflow.add_node("publish_results", publish_results)

    workflow.set_entry_point("fetch_transactions")
    workflow.add_edge("fetch_transactions", "run_matching_engine")
    workflow.add_edge("run_matching_engine", "publish_results")
    workflow.add_edge("publish_results", END)

    return workflow.compile()
