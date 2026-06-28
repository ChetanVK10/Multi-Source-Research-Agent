from functools import lru_cache
from typing import Any

from langgraph.graph import END, StateGraph

from app.graph.nodes.document_retriever import document_retriever_node
from app.graph.nodes.merge import merge_node
from app.graph.nodes.planner import planner_node
from app.graph.nodes.reranker import reranker_node
from app.graph.nodes.router import route_to_required_sources, router_node
from app.graph.nodes.sql_retriever import sql_retriever_node
from app.graph.nodes.synthesizer import synthesizer_node
from app.graph.nodes.web_retriever import web_retriever_node
from app.graph.state import ResearchGraphState


def phase_seven_terminal_node(state: ResearchGraphState) -> dict[str, Any]:
    return {"status": state.get("status", "completed")}


@lru_cache
def build_research_graph() -> Any:
    graph = StateGraph(ResearchGraphState)

    graph.add_node("planner", planner_node)
    graph.add_node("router", router_node)
    graph.add_node("documents", document_retriever_node)
    graph.add_node("web", web_retriever_node)
    graph.add_node("sql", sql_retriever_node)
    graph.add_node("merge", merge_node)
    graph.add_node("reranker", reranker_node)
    graph.add_node("synthesizer", synthesizer_node)
    graph.add_node("phase_seven_terminal", phase_seven_terminal_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "router")
    graph.add_conditional_edges(
        "router",
        route_to_required_sources,
        {
            "documents": "documents",
            "web": "web",
            "sql": "sql",
            "__end__": END,
        },
    )
    graph.add_edge("documents", "merge")
    graph.add_edge("web", "merge")
    graph.add_edge("sql", "merge")
    graph.add_edge("merge", "reranker")
    graph.add_edge("reranker", "synthesizer")
    graph.add_edge("synthesizer", "phase_seven_terminal")
    graph.add_edge("phase_seven_terminal", END)

    return graph.compile()
