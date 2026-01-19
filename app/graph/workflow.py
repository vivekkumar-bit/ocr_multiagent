from langgraph.graph import StateGraph
from typing import TypedDict

from app.agents.ocr_agent import ocr_agent
from app.agents.processor_agent import processor_agent
from app.agents.excel_agent import excel_agent

class GraphState(TypedDict):
    file_bytes: bytes
    file_type: str
    raw_text: str
    images: list
    final_json: str
    excel_file: bytes

def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("ocr", ocr_agent)
    graph.add_node("processor", processor_agent)
    graph.add_node("excel", excel_agent)

    graph.set_entry_point("ocr")
    graph.add_edge("ocr", "processor")
    graph.add_edge("processor", "excel")

    return graph.compile()
