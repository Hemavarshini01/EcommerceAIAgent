# 🛒 Ecommerce AI Agent

A local, privacy-first **AI question-answering API** over your sales data, powered by open-source LLMs (like Gemma with Ollama).

---

## 📦 Project Structure

```
ECOMMERCE_AI_AGENT/
├── data/
│   ├── ad_sales_metrics.csv
│   ├── all_metrics.db
│   ├── eligibility.csv
│   └── total_sales_metrics.csv
├
├── app.py
├── merge_to_sql.py
├── ollama
├── README.md
└── requirements.txt
```

---

## 🚀 Setup & Usage

### 1. Prerequisites

- Python 3.8+
- [Ollama](https://ollama.com/) installed (for local LLM inference)
- All your data CSVs inside the `data/` folder

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Merge CSVs and Build Database

```bash
python merge_to_sql.py
```
- This creates or updates `data/all_metrics.db` from your CSVs.

### 4. Pull & Run the LLM Model

In a new terminal:

```bash
ollama pull gemma:2b
ollama run gemma:2b
```
_(Keep this terminal running.)_

### 5. Start the API Server

In another terminal:

```bash
uvicorn app:app --reload
```

### 6. Ask Questions (Natural Language → SQL → Answer)

Use [http://localhost:8000/docs](http://localhost:8000/docs) for interactive testing, or try:

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"What is the total sales of the company?\"}"
```

### 7. Get Answers With Plots

For questions that should produce a plot (e.g. "Show daily total sales over time"):

```bash
curl -X POST "http://localhost:8000/ask_with_plot" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"Show daily total sales over time\"}"
```

If `"plot_url": "/plot"` is in the response, view [http://localhost:8000/plot](http://localhost:8000/plot) in your browser.

---

## 📊 How Plotting Works

If your SQL result includes fields `date` and `total_sales`, the API automatically generates a line plot and serves it at `/plot`.

---

## ⚡ Files Overview

- **data/**: All input CSVs and the generated SQLite database.
- **app.py**: FastAPI app (LLM → SQL → responses/plots).
- **merge_to_sql.py**: Merges your CSVs into the database.
- **requirements.txt**: Python dependencies.
- **README.md**: Project instructions.
- **.env**: _(Optional)_ For environment variables.
- **ollama**: _(Optional label/folder for local Ollama config)_

---

## 🛡️ Notes & Troubleshooting

- Ensure Ollama and the model are running (**keep ollama run window open**).
- If plotting, ensure your `date` column is parseable (ideally `YYYY-MM-DD` format).
- For dataset or model changes, re-run the relevant steps above.
- All LLM calls and plots run **fully locally**—your data never leaves your machine.

---

## 📚 Further Customizations

- Expand with new plot types by editing `app.py`.
- Switch to `Mistral`, `Phi-3`, or `Llama 3` by pulling with Ollama and changing the model string in `app.py`.

---

## 🤖 Get Help

If you run into issues, check logs in the terminal windows or [Ollama docs](https://ollama.com/). For project-specific issues, consult this README’s Troubleshooting section.

---
