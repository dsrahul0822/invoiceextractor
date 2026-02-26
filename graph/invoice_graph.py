from __future__ import annotations
from typing import Any, Dict, TypedDict, Optional

from langgraph.graph import StateGraph, END

from nodes.extract_node import extract_invoice_fields
from nodes.validate_node import validate_and_normalize
from nodes.excel_writer_node import write_to_excel


class InvoiceState(TypedDict, total=False):
    filename: str
    image_bytes: bytes

    raw_extraction: Dict[str, Any]
    invoice_data: Dict[str, Any]

    output_excel_path: str
    rows_written: int
    error: str


def build_invoice_graph():
    g = StateGraph(InvoiceState)

    g.add_node("extract", extract_invoice_fields)
    g.add_node("validate", validate_and_normalize)
    g.add_node("write_excel", write_to_excel)

    g.set_entry_point("extract")
    g.add_edge("extract", "validate")
    g.add_edge("validate", "write_excel")
    g.add_edge("write_excel", END)

    return g.compile()