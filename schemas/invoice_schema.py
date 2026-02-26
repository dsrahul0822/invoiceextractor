from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class InvoiceItem(BaseModel):
    item: str = Field(..., description="Line item name/description")
    quantity: Optional[float] = Field(None, description="Quantity as number")
    rate: Optional[float] = Field(None, description="Rate/price per unit as number")
    amount: Optional[float] = Field(None, description="Line item total amount as number")


class InvoiceData(BaseModel):
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None  # keep as string; we normalize later
    email: Optional[str] = None

    billed_by: Optional[str] = None
    billed_by_address: Optional[str] = None

    billed_to: Optional[str] = None
    billed_to_address: Optional[str] = None

    currency: Optional[str] = Field(None, description="Currency code or symbol, e.g., INR/₹")
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total: Optional[float] = None

    items: List[InvoiceItem] = Field(default_factory=list)