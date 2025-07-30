import streamlit as st
import time
import io
import os

from utils1 import (
    read_file,
    get_columns,
    get_rows_by_column_value,
    get_specific_value,
    extract_target_column,
    split_matching_rows,
    fill_template
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

    with st.expander("🔍 View First Matching Row"):
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
    first_row_dict = None

    # Safe retrieval of first_row_dict
    if query_result and isinstance(query_result, dict):
        first_row_dict = query_result.get("first_row_dict")

    if not first_row_dict and "first_row_dict" in st.session_state:
        first_row_dict = st.session_state["first_row_dict"]

    edited_data = {}

    with st.expander("📋 View Key-Value Table"):
        if first_row_dict:
            st.markdown("### 📝 Review & Edit Data Before Generating")

            # Let user edit fields before generating the document
            edited_data = {}
            for field, value in first_row_dict.items():
                edited_data[field] = st.text_input(field, value)

            # Optional: allow download after edit
            #template_path = "template.docx"
            #st.markdown("### 📥 Download Filled Template")
            # Save edited data to session state
            st.session_state["edited_data"] = edited_data

        else:
            st.warning("⚠️ No data available to generate document. Please run a query first.")
    # --------------------
    # 📄 Generate Button OUTSIDE the Expander
    # --------------------
    if "edited_data" in st.session_state:
        st.markdown("### 📄 Generate Document From Template")

        if st.button("📄 Generate From Template"):
            template_path = "template.docx"
            doc = fill_template(template_path, st.session_state["edited_data"])

            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            st.download_button(
                label="📥 Download DOCX",
                data=buffer,
                file_name="generated_from_template.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
else:
    st.info("Please upload a file to begin.")


