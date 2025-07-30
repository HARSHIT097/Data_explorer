from datetime import datetime
import pandas as pd
from docx import Document
import re
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import tempfile
import os

def generate_pdf_from_dict(data_dict):
    # Create a temporary file to save PDF
    temp_dir = tempfile.mkdtemp()
    pdf_path = os.path.join(temp_dir, "generated_output.pdf")

    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Generated PDF Report")

    y -= 30
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    y -= 40

    for key, value in data_dict.items():
        if y < 50:  # New page
            c.showPage()
            y = height - 50
        c.drawString(50, y, f"{key}: {value}")
        y -= 20

    c.save()
    return pdf_path


def generate_html_from_data(data_dict):
    html = "<html><body>"
    html += "<h2>Document Data</h2><ul>"
    for key, value in data_dict.items():
        html += f"<li><strong>{key}</strong>: {value}</li>"
    html += f"<li><strong>Date</strong>: {datetime.today().strftime('%d-%m-%Y')}</li>"
    html += "</ul></body></html>"
    return html
def read_file(file):
    try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file, dtype=str)
            elif file.name.endswith('.xlsx'):
                df = pd.read_excel(file, dtype=str, engine='openpyxl')  # 👈 important fix
            else:
                raise ValueError("Unsupported file format")
            return df[:10]
    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
        return pd.DataFrame()

# 📋 List column names
def get_columns(df):
    return list(df.columns)

# 🔍 Filter rows based on column name and value
def get_rows_by_column_value(df, column_name, value):
    if column_name not in df.columns:
        return f"❌ Column '{column_name}' not found in data."

    # Handle pandas Series mistakenly passed as value
    if isinstance(value, pd.Series):
        if not value.empty:
            value = value.iloc[0]
        else:
            return "❌ Empty value provided for filtering."

    try:
        filtered = df[df[column_name] == value]
        if filtered.empty:
            return f"🔍 No rows found where '{column_name}' == {value}"
        return filtered.to_dict(orient="index")
    except Exception as e:
        return f"❌ Error while filtering: {str(e)}"

# 🎯 Extract specific column values from filtered data
def get_specific_value(df, filters: dict, target_column: str):
    if target_column not in df.columns:
        return {"error": f"❌ Target column '{target_column}' not found."}

    filtered = df.copy()

    for col, val in filters.items():
        if col not in df.columns:
            return {"error": f"❌ Filter column '{col}' not found."}

        if isinstance(val, pd.Series):
            if not val.empty:
                val = val.iloc[0]
            else:
                return {"error": f"❌ Empty value in filter for '{col}'."}

        filtered = filtered[filtered[col] == val]

    if filtered.empty:
        return {"message": f"🔍 No matching rows found with given filters."}

    return filtered[target_column].to_dict()

# ✂️ Get random or sequential subset
def get_subset(df, num_rows, num_cols, random=True):
    if random:
        df_subset = df.sample(n=min(num_rows, len(df))).sample(n=min(num_cols, len(df.columns)), axis=1)
    else:
        df_subset = df.iloc[:num_rows, :num_cols]
    return df_subset

# 🎯 Extract value from dict
def extract_target_column(filtered_dict: dict, target_column: str):
    if not filtered_dict:
        return {"error": "❌ Input dictionary is empty."}

    result = {}

    for idx, row in filtered_dict.items():
        if target_column not in row:
            return {"error": f"❌ Column '{target_column}' not found in row {idx}."}
        result[idx] = row[target_column]

    key, value = next(iter(result.items()))
    return value


def split_matching_rows(filtered_dict: dict):
    if not filtered_dict:
        return None, None

    df = pd.DataFrame.from_dict(filtered_dict, orient='index')
    first_row_df = df.iloc[[0]]
    machine_rows_df = df.iloc[1:]
    return first_row_df, machine_rows_df

def fill_template(template_path, data_dict):
    doc = Document(template_path)

    # Inject today's date into data
    data_dict["Date"] = datetime.today().strftime("%d-%m-%Y")

    # Replace in paragraphs
    for para in doc.paragraphs:
        for key, val in data_dict.items():
            placeholder = f"{{{key}}}"
            if placeholder in para.text:
                para.text = para.text.replace(placeholder, str(val))
                print(placeholder)
    return doc
