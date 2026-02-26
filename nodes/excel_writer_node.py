from __future__ import annotations
import os
from typing import Any, Dict, List

import pandas as pd


def write_to_excel(state: Dict[str, Any]) -> Dict[str, Any]:
    invoice = state.get("invoice_data") or {}
    output_path = state.get("output_excel_path") or os.getenv("OUTPUT_EXCEL_PATH", "outputs/invoices.xlsx")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    items: List[dict] = invoice.get("items", []) or []

    # One-row-per-line-item (simple + best for filtering)
    rows = []
    if items:
        for it in items:
            rows.append(
                {
                    "invoice_number": invoice.get("invoice_number"),
                    "invoice_date": invoice.get("invoice_date"),
                    "email": invoice.get("email"),
                    "billed_by": invoice.get("billed_by"),
                    "billed_by_address": invoice.get("billed_by_address"),
                    "billed_to": invoice.get("billed_to"),
                    "billed_to_address": invoice.get("billed_to_address"),
                    "currency": invoice.get("currency"),
                    "subtotal": invoice.get("subtotal"),
                    "tax": invoice.get("tax"),
                    "total": invoice.get("total"),
                    "item": it.get("item"),
                    "quantity": it.get("quantity"),
                    "rate": it.get("rate"),
                    "amount": it.get("amount"),
                }
            )
    else:
        # still write a row (invoice-level only)
        rows.append(
            {
                "invoice_number": invoice.get("invoice_number"),
                "invoice_date": invoice.get("invoice_date"),
                "email": invoice.get("email"),
                "billed_by": invoice.get("billed_by"),
                "billed_by_address": invoice.get("billed_by_address"),
                "billed_to": invoice.get("billed_to"),
                "billed_to_address": invoice.get("billed_to_address"),
                "currency": invoice.get("currency"),
                "subtotal": invoice.get("subtotal"),
                "tax": invoice.get("tax"),
                "total": invoice.get("total"),
                "item": None,
                "quantity": None,
                "rate": None,
                "amount": None,
            }
        )

    df_new = pd.DataFrame(rows)

    if os.path.exists(output_path):
        df_old = pd.read_excel(output_path)
        df_all = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_all = df_new

    df_all.to_excel(output_path, index=False)
    state["output_excel_path"] = output_path
    state["rows_written"] = len(df_new)
    return state