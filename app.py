import os
import sqlite3
import requests
import re
import matplotlib.pyplot as plt
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

DB_PATH = os.path.join("data", "all_metrics.db")
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma:2b"

app = FastAPI()

@app.get("/")
def root():
    return {"message": "🎉 Local AI ready! Use POST /ask or /ask_with_plot to query the data."}

class QuestionRequest(BaseModel):
    question: str

def get_db_schema():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(all_metrics);")
        cols = cur.fetchall()
    schema = "Table ALL_METRICS columns:\n" + ", ".join([f"{c[1]} ({c[2]})" for c in cols])
    return schema

def call_gemma(prompt: str):
    data = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    response = requests.post(OLLAMA_API_URL, json=data)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Ollama error: {response.text}")
    return response.json().get("response", "").strip()

def clean_sql(llm_output: str) -> str:
    sql = re.sub(r"^``````", "").strip()
    return sql

def question_to_sql(question, schema):
    prompt = (
        f"You are an expert data analyst. Given the schema: {schema}\n"
        f"Convert this question into a valid SQLite SQL query on the 'all_metrics' table. "
        f"Respond with ONLY the SQL query (no Markdown/code block):\n"
        f"{question}"
    )
    llm_output = call_gemma(prompt)
    sql = clean_sql(llm_output)
    return sql

def fetch_sql(sql):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]
        return [dict(zip(colnames, row)) for row in rows], colnames
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SQL Execution Error: {str(e)}")

def results_to_natural(question, results):
    if not results:
        return "No data found for your query."
    prompt = (
        f"For the question: '{question}', summarize these SQL results in clear, non-technical language:\n"
        f"{results}"
    )
    return call_gemma(prompt)

@app.post("/ask")
def ask_question(request: QuestionRequest):
    schema = get_db_schema()
    sql = question_to_sql(request.question, schema)
    results, columns = fetch_sql(sql)
    answer = results_to_natural(request.question, results)
    return JSONResponse({
        "question": request.question,
        "sql": sql,
        "data": results,
        "answer": answer
    })

@app.post("/ask_with_plot")
def ask_with_plot(request: QuestionRequest):
    schema = get_db_schema()
    sql = question_to_sql(request.question, schema)
    results, columns = fetch_sql(sql)
    answer = results_to_natural(request.question, results)
    
    # Attempt to extract 'date' and 'total_sales' lists for plotting
    dates = [row['date'] for row in results if 'date' in row and row['date'] is not None]
    sales = [row['total_sales'] for row in results if 'total_sales' in row and row['total_sales'] is not None]
    if dates and sales:
        plt.figure(figsize=(8,4))
        plt.plot(dates, sales, marker='o')
        plt.xlabel('Date')
        plt.ylabel('Total Sales')
        plt.title('Total Sales Over Time')
        plt.tight_layout()
        plot_path = "data/plot.png"
        plt.savefig(plot_path)
        plt.close()
        return {
            "question": request.question,
            "sql": sql,
            "data": results,
            "answer": answer,
            "plot_url": "/plot"
        }
    else:
        return {
            "question": request.question,
            "sql": sql,
            "data": results,
            "answer": answer,
            "plot_url": None
        }

@app.get("/plot")
def get_plot():
    plot_path = "data/plot.png"
    if not os.path.exists(plot_path):
        raise HTTPException(status_code=404, detail="No plot found for last query.")
    return FileResponse(plot_path)
