import os
import streamlit as st
from dotenv import load_dotenv
from PIL import Image

from graph.invoice_graph import build_invoice_graph

load_dotenv()

st.set_page_config(page_title="Invoice Extractor (LangGraph + OpenAI)", layout="wide")

st.title("🧾 Invoice Extractor")
st.caption("Upload an invoice image → Extract fields using OpenAI Vision → Save into Excel")

app = build_invoice_graph()

uploaded = st.file_uploader("Upload invoice image", type=["png", "jpg", "jpeg"])

col1, col2 = st.columns([1, 1])

if uploaded:
    with col1:
        st.subheader("Preview")
        img = Image.open(uploaded)
        st.image(img, use_container_width=True)

    with col2:
        st.subheader("Run Extraction")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        st.write(f"**Model:** {model}")

        if st.button("🚀 Extract & Save to Excel", type="primary"):
            with st.spinner("Reading invoice and extracting fields..."):
                try:
                    result = app.invoke(
                        {
                            "filename": uploaded.name,
                            "image_bytes": uploaded.getvalue(),
                            "output_excel_path": os.getenv("OUTPUT_EXCEL_PATH", "outputs/invoices.xlsx"),
                        }
                    )

                    st.success(f"Done! Rows written: {result.get('rows_written', 0)}")

                    st.subheader("Extracted JSON")
                    st.json(result.get("invoice_data", {}))

                    st.subheader("Excel Output")
                    excel_path = result.get("output_excel_path", "outputs/invoices.xlsx")
                    st.write(f"Saved to: `{excel_path}`")

                    # download button
                    with open(excel_path, "rb") as f:
                        st.download_button(
                            label="⬇️ Download Excel",
                            data=f,
                            file_name=os.path.basename(excel_path),
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        )

                except Exception as e:
                    st.error(f"Extraction failed: {e}")

else:
    st.info("Upload an invoice image to begin.")