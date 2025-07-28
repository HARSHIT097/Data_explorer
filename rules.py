def respond_to_query(query, df):
    query = query.lower()
    if "columns" in query:
        return f"Available columns: {', '.join(df.columns)}"
    elif "rows" in query:
        return f"Total rows: {len(df)}"
    else:
        return "Try asking about columns or number of rows."
