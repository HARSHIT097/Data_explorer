import pandas as pd
import os
import openpyxl


def read_file(file_path):
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format")
    return df


def get_columns(df):
    return list(df.columns)


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


def get_specific_value(df, filters: dict, target_column: str):
    # Step 1: Check if target column exists
    if target_column not in df.columns:
        return {"error": f"❌ Target column '{target_column}' not found."}

    filtered = df.copy()

    # Step 2: Apply filters
    for col, val in filters.items():
        if col not in df.columns:
            return {"error": f"❌ Filter column '{col}' not found."}

        # Handle if value is a Series
        if isinstance(val, pd.Series):
            if not val.empty:
                val = val.iloc[0]
            else:
                return {"error": f"❌ Empty value in filter for '{col}'."}

        filtered = filtered[filtered[col] == val]

    # Step 3: Return matched values from target column
    if filtered.empty:
        return {"message": f"🔍 No matching rows found with given filters."}

    return filtered[target_column].to_dict()


def get_subset(df, num_rows, num_cols, random=True):
    if random:
        df_subset = df.sample(n=num_rows).sample(n=num_cols, axis=1)
    else:
        df_subset = df.iloc[:num_rows, :num_cols]
    return df_subset


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

def generate_email_from_row(row):
    return f"""
    Dear {row.get('CUST_ID')},

    Thank you for your recent transaction. Your current balance is {row.get('BALANCE')}.
    Your total purchases are {row.get('PURCHASES')}.

    Regards,
    YourBank Team
    """
