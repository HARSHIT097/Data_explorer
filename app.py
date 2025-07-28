import streamlit as st
import pandas as pd
import time
import io
import os
from docx import Document

from utils1 import (
    read_file,
    get_columns,
    get_rows_by_column_value,
    get_specific_value,
    extract_target_column,
    split_matching_rows
)

# App Config
st.set_page_config(page_title="📄 Data Chat Query", layout="wide")
st.title("📊 Data Chat + Document Generator")
st.caption("🚀 Built by Harshit | Rule-based + Extendable chatbot")

# --------------------
# 📁 File Handling
# --------------------
st.sidebar.header("Upload & Query Options")

uploaded_file = st.sidebar.file_uploader("📁 Upload CSV or Excel", type=["csv", "xlsx"])
DEFAULT_FILE = "sample_data.xlsx"  # Ensure this file exists

if uploaded_file:
    st.session_state["latest_file"] = uploaded_file
elif "latest_file" not in st.session_state and os.path.exists(DEFAULT_FILE):
    st.session_state["latest_file"] = open(DEFAULT_FILE, "rb")

file_to_use = st.session_state.get("latest_file", None)

# --------------------
# 📄 Load File with Cache
# --------------------
@st.cache
def load_data(file):
    return read_file(file)

if file_to_use:
    with st.spinner("📄 Loading file..."):
        df = load_data(file_to_use)
        time.sleep(0.5)

    st.subheader("🔍 Sample Data")
    st.dataframe(df.head(10))

    columns = get_columns(df)

    # --------------------
    # 🧠 Sidebar Inputs
    # --------------------
    st.sidebar.markdown("## 🧠 Query Parameters")
    selected_column = st.sidebar.selectbox("Select column to filter by", columns)
    filter_value = st.sidebar.text_input(f"Enter value for {selected_column}")
    target_column = st.sidebar.selectbox("Target column to retrieve", columns)

    # ----------------------------
    # 📥 Query Execution (Sidebar)
    # ----------------------------
    if st.sidebar.button("Query Data"):
        with st.spinner("🔍 Filtering and fetching data..."):
            progress = st.progress(0)
            result_dict = get_rows_by_column_value(df, selected_column, filter_value)
            time.sleep(0.3)
            progress.progress(30)

            if isinstance(result_dict, dict) and result_dict:
                first_df, machine_df = split_matching_rows(result_dict)
                time.sleep(0.3)
                progress.progress(60)

                first_row_dict = {}
                if first_df is not None and not first_df.empty:
                    first_row_dict = first_df.iloc[0].to_dict()

                st.session_state["query_result"] = {
                    "first_df": first_df,
                    "machine_df": machine_df,
                    "first_row_dict": first_row_dict,
                    "target_value": extract_target_column(result_dict, target_column),
                }

                progress.progress(100)
                st.success("✅ Query Successful")
            else:
                st.session_state["query_result"] = None
                st.error("❌ No matching data found for that filter.")

    # ----------------------------
    # 📊 Display Query Results
    # ----------------------------
    query_result = st.session_state.get("query_result", None)

    if query_result:
        first_df = query_result["first_df"]
        machine_df = query_result["machine_df"]
        first_row_dict = query_result["first_row_dict"]
        target_value = query_result["target_value"]

        # 🧾 First Match
        st.subheader("🧾 First Matching Row")
        if first_df is not None and not first_df.empty:
            st.dataframe(first_df)
        else:
            st.info("No matching rows to display.")

        # 🤖 Machine Matches
        st.subheader("🤖 Machine-Matched Rows")
        if machine_df is not None and not machine_df.empty:
            st.dataframe(machine_df)

            st.download_button(
                label="📥 Download Machine-Matched Rows (CSV)",
                data=machine_df.to_csv(index=False),
                file_name="machine_matched_rows.csv",
                mime="text/csv"
            )
        else:
            st.info("No machine-matched rows found.")

        # 🎯 Target Column Value
        st.markdown(f"### 🎯 Target Value from `{target_column}`")
        if target_value:
            st.code(target_value)
        else:
            st.warning("⚠️ No target value found.")
    else:
        st.info("ℹ️ Run a query to view results.")

    # --------------------
    # 📄 Generate Document
    # --------------------
    st.markdown("---")
    st.markdown("## 📝 Generate Document")
    query_result = st.session_state.get("query_result", None)

    if query_result and query_result.get("first_row_dict"):
    #if 'first_row_dict' in st.session_state:
        first_row_dict = query_result['first_row_dict']

        doc_template = f"""
            Dear Customer {first_row_dict.get("CUST_ID", "N/A")},
    
            We are writing to inform you of your latest financial activity:
    
            - 💰 Balance: {first_row_dict.get("BALANCE", "N/A")}
            - 📊 Balance Frequency: {first_row_dict.get("BALANCE_FREQUENCY", "N/A")}
            - 🛍️ Purchases: {first_row_dict.get("PURCHASES", "N/A")}
    
            Thank you for choosing our service.
    
            Regards,  
            💼 Your DataBot
            """

        st.text_area("📄 Document Preview", doc_template, height=250)
        st.markdown("### 📥 Download Document As")

        download_format = st.selectbox("Choose format", ["TXT", "DOCX"], key="format_select")
        generate_button = st.button("📄 Generate & Download")

        if generate_button:
            if download_format == "TXT":
                buffer = io.StringIO()
                buffer.write(doc_template)
                st.download_button(
                    label="📥 Download TXT",
                    data=buffer.getvalue(),
                    file_name="generated_document.txt",
                    mime="text/plain"
                )

            elif download_format == "DOCX":
                doc = Document()
                for line in doc_template.strip().split("\n"):
                    doc.add_paragraph(line.strip())

                buffer = io.BytesIO()
                doc.save(buffer)
                buffer.seek(0)

                st.download_button(
                    label="📥 Download DOCX",
                    data=buffer,
                    file_name="generated_document.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
    else:
        st.error("⚠️ No data available to generate document. Please run a query first.")
else:
    st.info("Please upload a file to begin.")
