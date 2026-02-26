from __future__ import annotations
import base64
import json
import os
from typing import Any, Dict

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def _image_bytes_to_data_url(image_bytes: bytes, filename: str) -> str:
    # basic mime inference
    ext = (filename.split(".")[-1] or "").lower()
    mime = "image/png" if ext in ("png",) else "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def extract_invoice_fields(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node:
    Input: state["image_bytes"], state["filename"]
    Output: state["raw_extraction"] (dict)
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY. Put it in .env")

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI(api_key=api_key)

    image_bytes: bytes = state["image_bytes"]
    filename: str = state.get("filename", "invoice.png")
    img_data_url = _image_bytes_to_data_url(image_bytes, filename)

    # Strong prompt for strict JSON extraction
    prompt = """
You are an invoice data extraction engine.

TASK:
Extract invoice details from the provided invoice image and return ONLY valid JSON.
Do NOT add any commentary, markdown, or extra keys.

OUTPUT JSON SCHEMA (exact keys):
{
  "invoice_number": string|null,
  "invoice_date": string|null,
  "email": string|null,

  "billed_by": string|null,
  "billed_by_address": string|null,

  "billed_to": string|null,
  "billed_to_address": string|null,

  "currency": string|null,
  "subtotal": number|null,
  "tax": number|null,
  "total": number|null,

  "items": [
    {"item": string, "quantity": number|null, "rate": number|null, "amount": number|null}
  ]
}

RULES:
- If a field is missing, use null.
- Always return "items" as an array (empty array if none).
- Numbers must be raw numbers (no commas, no currency symbol). Example: "₹3,000.00" -> 3000.00
- Keep invoice_date as the same text you see (we will normalize later).
"""

    resp = client.responses.create(
        model=model,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": img_data_url},
                ],
            }
        ],
    )

    text = (resp.output_text or "").strip()

    # Sometimes models may wrap JSON with extra text; attempt robust extraction
    json_obj = None
    try:
        json_obj = json.loads(text)
    except Exception:
        # try to extract first {...} block
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = text[start : end + 1]
            json_obj = json.loads(candidate)
        else:
            raise RuntimeError(f"Model did not return JSON. Output was:\n{text}")

    state["raw_extraction"] = json_obj
    return state