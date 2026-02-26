from __future__ import annotations
import re
from datetime import datetime
from typing import Any, Dict, Optional

from schemas.invoice_schema import InvoiceData


def _to_float(x: Any) -> Optional[float]:
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip()
    if not s:
        return None
    # remove currency symbols/commas
    s = re.sub(r"[^\d.\-]", "", s)
    if s in ("", ".", "-", "-."):
        return None
    try:
        return float(s)
    except Exception:
        return None


def _normalize_date(date_str: Optional[str]) -> Optional[str]:
    if not date_str:
        return None
    s = date_str.strip()

    # Try common formats quickly
    fmts = [
        "%b %d, %Y",   # Jan 23, 2025
        "%B %d, %Y",   # January 23, 2025
        "%d %b %Y",    # 23 Jan 2025
        "%d %B %Y",    # 23 January 2025
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%m/%d/%Y",
    ]
    for f in fmts:
        try:
            dt = datetime.strptime(s, f)
            return dt.strftime("%Y-%m-%d")
        except Exception:
            pass

    # If not parseable, return original
    return s


def validate_and_normalize(state: Dict[str, Any]) -> Dict[str, Any]:
    raw = state.get("raw_extraction") or {}

    # Pydantic validation (also ensures items structure exists)
    invoice = InvoiceData.model_validate(raw)

    # Normalize numeric fields
    invoice.subtotal = _to_float(invoice.subtotal)
    invoice.tax = _to_float(invoice.tax)
    invoice.total = _to_float(invoice.total)

    for it in invoice.items:
        it.quantity = _to_float(it.quantity)
        it.rate = _to_float(it.rate)
        it.amount = _to_float(it.amount)

    # Normalize date
    invoice.invoice_date = _normalize_date(invoice.invoice_date)

    state["invoice_data"] = invoice.model_dump()
    return state