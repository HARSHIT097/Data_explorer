from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil, os, json
import pandas as pd
#from parser import (read_file, get_columns, get_rows_by_column_value, get_specific_value, extract_target_column)
from data_utils import (
    read_file, get_columns, get_rows_by_column_value,
    get_specific_value, extract_target_column
)

app = FastAPI()
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

df_store = {}  # cache df in-memory

@app.get("/")
def read_root():
    return {"message": "✅ FastAPI backend is running. Use /upload and /query endpoints."}


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    df = read_file(file_path)
    df_store['df'] = df
    return {"columns": get_columns(df), "message": "✅ File uploaded successfully."}

@app.post("/query/")
async def query_data(
    target_column: str = Form(...),
    filter_column: str = Form(...),
    filter_value: str = Form(...)
):
    df = df_store.get("df")
    if df is None:
        return JSONResponse(status_code=400, content={"error": "No file uploaded."})

    rows = get_rows_by_column_value(df, filter_column, filter_value)
    if isinstance(rows, str):
        return {"error": rows}

    value = extract_target_column(rows, target_column)
    return {
        "value": value,
        "rows": rows
    }
