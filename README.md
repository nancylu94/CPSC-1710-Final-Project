# **CPSC-1710 Final Project**

## **Automotive Financial & Sustainability Analysis Tool**

A retrieval-augmented analysis system that evaluates **financial performance**, **sustainability disclosures**, and **EV-transition readiness** for automotive manufacturers.
Built with **LangChain**, **FAISS**, **RAG**, and **OpenAI LLMs**, with a clean Streamlit front-end.

---

# **Table of Contents**

1. [Overview](#overview)
2. [Scoring Framework](#scoring-framework)
3. [How the Tool Works](#how-the-tool-works)
4. [Running the Tool](#running-the-tool)
5. [Reproducing Results](#reproducing-results)
6. [Installation & Setup](#installation--setup)

---

# **Overview**

This tool analyzes two types of reports:

1. **Financial Report** (10-K / annual report)
2. **Sustainability / ESG Report**

It produces:

* A **financial score** (0–16 → normalized to 10)
* A **sustainability score** (0–17 → normalized to 10)
* A combined **overall score (0–10)**
* A **1-page investor summary**
* A **RAG-powered chat assistant** that answers follow-up questions about the reports

The system is designed specifically for **automotive manufacturers**, evaluating transparency, climate metrics, EV strategy, and operational risk.

---

# **Scoring Framework**

## **Financial Indicators (16 points → normalized to 10)**

Each category scored 0–2:

* Revenue growth
* Gross margin
* Operating margin
* EBITDA margin
* Free cash flow
* CapEx % of revenue
* R&D % of revenue
* Inventory / Days Inventory Outstanding

## **Sustainability Indicators (17 points → normalized to 10)**

Four categories:

* **GHG Reporting** (Scope 1/2/3 + YoY change)
* **Automotive Transition Metrics** (EV targets, battery recycling, ICE phase-out, traceability)
* **Disclosure Quality** (specificity, evidence, non-promotional)
* **Environmental & Compliance Metrics** (water, waste, fines, supplier audits, incidents)

These match the scoring rules in:

* `FINANCIAL_CRITERIA.md`
* `SUSTAINABILITY_CRITERIA.md`

---

# **How the Tool Works**

### **1. PDF Loading & Chunking**

Reports are split into semantically meaningful text chunks.

### **2. Vector Embedding & FAISS Indexing**

Embeddings are generated using `OpenAIEmbeddings` and stored in FAISS for similarity search.

### **3. Multi-Query RAG Retrieval**

For each section, the tool runs several targeted queries, including:

* Income statement / margins
* Cash flow / CapEx / R&D
* Sustainability claims
* GHG emissions
* Supply chain & EV transition metrics

All retrieved text is consolidated and fed to the LLM.

### **4. Indicator Extraction**

The LLM extracts structured indicators with supporting evidence.

### **5. Scoring & Summary Generation**

The tool:

* Computes financial and sustainability scores
* Normalizes scores to 10-point scales
* Produces a clear investor-ready summary

### **6. Optional Chat Assistant (Streamlit)**

Users can ask:

* “Why did the company score poorly on R&D?”
* “What does the report say about battery recycling?”
* “Find mentions of supply-chain emissions.”

The assistant uses RAG automatically when needed.

---

# **Running the Tool**

## **Option A — Streamlit Web App (Recommended)**

```bash
streamlit run app.py
```

In the interface:

1. Enter your OpenAI API key
2. Upload financial and/or sustainability PDFs
3. Click **Analyze Reports**
4. View:

   * Scores
   * Breakdown
   * Investor summary
   * Disclosure quality matrix
   * Chat assistant (RAG-enabled)

---

## **Option B — Command Line**

Edit two lines in `main.py`:

```python
FINANCIAL_PDF_PATH = "data/your_financial_report.pdf"
SUSTAINABILITY_PDF_PATH = "data/your_sustainability_report.pdf"
```

Run:

```bash
python main.py
```

Outputs appear in the terminal:

* Scores
* Evidence
* Full investor summary

---

# **Reproducing Results**

Sample files (included in `data/`):

* `AAPL_2024_Annual_Report_Condensed.pdf`
* `RIVN_2024_Environmental_Metrics_Report.pdf`

## **To reproduce the example output:**

### **Web App**

1. `streamlit run app.py`
2. Upload the two sample PDFs
3. Run analysis (takes ~2–3 minutes)

### **CLI**

Ensure `main.py` uses the sample paths:

```python
FINANCIAL_PDF_PATH = "data/AAPL_2024_Annual_Report_Condensed.pdf"
SUSTAINABILITY_PDF_PATH = "data/RIVN_2024_Environmental_Metrics_Report.pdf"
```

Then run:

```bash
python main.py
```

Expected behavior:

* Apple financial score: ~10–14
* Rivian sustainability score: ~12–16
* Overall combined score: ~7–9

---

# **Installation & Setup**

### **Prerequisites**

* Python **3.11**
* OpenAI API key
* pip

### **1. Create a virtual environment**

macOS/Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### **2. Install dependencies**

```bash
pip install -r requirements.txt
```

### **3. Add your OpenAI API key**

Create `.env`:

```
OPENAI_API_KEY=your_api_key_here
```

### **4. (Optional) Add PDFs to `/data` directory**

For CLI mode only.