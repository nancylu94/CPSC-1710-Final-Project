# CPSC-1710-Final-Project
Financial/Sustainability Analysis Tool for Introduction to AI Applications

## Table of Contents

- [Overview](#overview)
- [Scoring Structure](#scoring-structure)
  - [Financial Indicators (16 points)](#financial-indicators-16-points--normalized-to-10)
  - [Sustainability Indicators (17 points)](#sustainability-indicators-16-points--normalized-to-10)
- [How the Tool Works](#how-the-tool-works)
- [Output Format](#output-format)
- [Use Cases](#use-cases)
- [Running the Code](#running-the-code)
  - [Option 1: Web Interface (Recommended)](#option-1-web-interface-recommended)
  - [Option 2: Command Line Interface](#option-2-command-line-interface)
- [Reproducing Results](#reproducing-results)
  - [Sample Data Included](#sample-data-included)
  - [Quick Start: Reproduce Sample Results](#quick-start-reproduce-sample-results)
  - [Expected Results for Sample Data](#expected-results-for-sample-data)
  - [Reproducing with Your Own Data](#reproducing-with-your-own-data)
  - [Validating Results](#validating-results)
  - [Batch Processing Multiple Companies](#batch-processing-multiple-companies)
  - [Cost Estimation](#cost-estimation)
- [Installation & Setup Guide](#installation--setup-guide)
  - [Prerequisites](#prerequisites)
  - [Step 1: Clone or Download the Repository](#step-1-clone-or-download-the-repository)
  - [Step 2: Create a Virtual Environment](#step-2-create-a-virtual-environment-recommended)
  - [Step 3: Install Dependencies](#step-3-install-dependencies)
  - [Step 4: Configure Environment Variables](#step-4-configure-environment-variables)
  - [Step 5: Prepare Sample Data](#step-5-prepare-sample-data-for-cli-option)
  - [Step 6: Verify Installation](#step-6-verify-installation)
  - [Troubleshooting Common Issues](#troubleshooting-common-issues)

---

# Automotive-Specific Financial & Sustainability Criteria

## Overview
This tool has been customized to assess **automotive manufacturers** specifically, with sustainability criteria tailored to the EV transition and automotive industry challenges.

## Scoring Structure

### Financial Indicators (16 points → normalized to 10)

#### 1. Revenue Growth (2 points)
- 2: Revenue increased >5% year-over-year
- 1: Revenue increased 0-5% year-over-year
- 0: Revenue declined or flat

**Why this matters:** Strong revenue growth indicates market share gains and successful product adoption, particularly important as automakers transition from ICE to EV platforms.

---

#### 2. Gross Margin (2 points)
- 2: Gross margin is positive AND improved year-over-year
- 1: Gross margin is positive but declined OR negative but improved year-over-year
- 0: Gross margin is negative AND did not improve (flat or worse)

**Why this matters:** Improving gross margins demonstrate pricing power and manufacturing efficiency, critical as EV production scales and battery costs decline.

---

#### 3. Operating Margin (2 points)
- 2: Operating margin is positive AND improved year-over-year
- 1: Operating margin is positive but declined OR negative but improved year-over-year
- 0: Operating margin is negative AND did not improve (flat or worse)

**Why this matters:** Operating margin improvement shows effective cost management during the capital-intensive EV transition period.

---

#### 4. EBITDA Margin (2 points)
- 2: EBITDA margin is positive AND improved year-over-year
- 1: EBITDA margin is positive but declined OR negative but improved year-over-year
- 0: EBITDA margin is negative AND did not improve (flat or worse)

**Why this matters:** EBITDA margin reveals core operational profitability before accounting for heavy depreciation from manufacturing investments.

---

#### 5. Free Cash Flow (2 points)
- 2: FCF is clearly positive
- 1: FCF is around break-even (0 to -5% of revenue)
- 0: FCF is clearly negative (worse than -5% of revenue)

**Why this matters:** Positive FCF demonstrates the company's ability to self-fund EV development and expansion without excessive capital raises.

---

#### 6. CapEx as % of Revenue (2 points)
- 2: CapEx is 3-8% of revenue (healthy range)
- 1: CapEx is 8-12% of revenue (aggressive but acceptable)
- 0: CapEx is <3% (under-investing) OR >12% (very heavy spending)

**Why this matters:** Balanced CapEx spending indicates sustainable investment in EV production capacity and battery technology without over-leveraging.

---

#### 7. R&D as % of Revenue (2 points)
- 2: R&D is 4-10% of revenue
- 1: R&D is 2-4% of revenue (minimal but acceptable)
- 0: R&D is <2% (under-investing) OR >10% (very high)

**Why this matters:** Adequate R&D investment ensures competitiveness in battery technology, autonomous driving, and next-generation EV platforms.

---

#### 8. Inventory & Days Inventory Outstanding (2 points)
- 2: DIO <40 days OR inventory lean/tightly managed
- 1: DIO 40-70 days OR inventory normal/acceptable
- 0: DIO >70 days OR inventory clearly elevated/excess

**Why this matters:** Low DIO indicates efficient inventory management and reduced risk of obsolescence as the industry rapidly shifts from ICE to EV vehicles.

### Sustainability Indicators (16 points → normalized to 10)

#### 1. GHG Emissions Reporting (4 points)
- ✓ Scope 1 emissions reported with numeric values
- ✓ Scope 2 emissions reported with numeric values
- ✓ Scope 3 emissions reported with numeric values
- ✓ Year-on-year change in emissions reported

**Why this matters:** Comprehensive GHG reporting demonstrates transparency and accountability for climate impact across the value chain.

---

#### 2. Automotive-Specific Targets & Progress (4 points)
- ✓ EV production targets/percentages specified
- ✓ Battery recycling rates or programs documented
- ✓ ICE (Internal Combustion Engine) phase-out date provided
- ✓ Supply chain traceability systems documented

**Why this matters:** These metrics show concrete commitment to the EV transition and circular economy principles specific to automotive manufacturing.

---

#### 3. Transparency & Anti-Greenwashing (3 points)
- ✓ Claims have specificity (dates, numbers, timelines)
- ✓ Claims have supporting evidence (data, third-party verification)
- ✓ Avoids excessive self-praise (factual vs promotional language)

**Examples of greenwashing red flags:**
- ❌ Vague: "Committed to sustainability" (no timeline)
- ❌ Aspirational: "Striving for net-zero" (no concrete plan)
- ❌ Self-praise: "World-leading in green manufacturing" (no evidence)

**Examples of good disclosure:**
- ✅ "Target 50% EV sales by 2030"
- ✅ "Reduced Scope 1 emissions by 12% YoY, verified by third-party auditor"
- ✅ "70% of energy from renewable sources in 2024, up from 58% in 2023"

---

#### 4. Environmental & Compliance Metrics (5 points)
- ✓ Water usage metrics disclosed
- ✓ Hazardous waste metrics disclosed
- ✓ Regulatory fines/violations disclosed
- ✓ Supplier audit frequency mentioned
- ✓ Product recalls (safety/environmental) or worker/plant incidents disclosed

**Why this matters:** These operational metrics reveal environmental management maturity and regulatory compliance beyond just carbon emissions. Product recalls and workplace incidents demonstrate transparency around operational risks.

---

## How the Tool Works

### Multi-Pass Retrieval & Analysis

**Financial Analysis:**
- Builds a vector store from the uploaded financial report and runs **4 targeted retrieval queries**  
  (income statement, balance sheet, cash flow/CapEx/FCF, and MD&A / narrative trends).
- Combines the retrieved chunks into a **single reduced context**, then runs one extraction pass (no further RAG).
- Extracts **8 financial indicators** with numeric scoring (0–2 points each), for a total of **16 points**.

**Sustainability Analysis:**
The tool uses **3 separate retrieval queries** to ensure comprehensive coverage:

1. **GHG Query** – Scope 1/2/3 emissions and year-on-year changes
2. **Automotive Transition Query** – EV production, battery recycling, ICE phase-out, supply-chain traceability
3. **Quality & Compliance Query** – sustainability claims, water usage, hazardous waste, regulatory fines, supplier audits, product recalls, safety incidents, worker safety

All retrieved contexts are combined before analysis so the LLM has the relevant evidence for all **16 sustainability criteria**.


---

## Output Format

### Scores Display
```
Financial score: X / 16 (normalized: Y / 10)
  - Revenue Growth: A / 2
  - Gross Margin: B / 2
  - Operating Margin: C / 2
  - EBITDA Margin: D / 2
  - Free Cash Flow: E / 2
  - CapEx % of Revenue: F / 2
  - R&D % of Revenue: G / 2
  - Inventory/DIO: H / 2

Sustainability score: Z / 16 (normalized: W / 10)
  - GHG Emissions: I / 4
  - Automotive Targets: J / 4
  - Transparency: K / 3
  - Environmental/Compliance: L / 5

Overall score: M / 10
```

### Investor Summary
Tailored to automotive industry with focus on:
- **Financial health:** Revenue growth, profitability margins (gross, operating, EBITDA), cash flow generation, capital allocation (CapEx, R&D), and inventory efficiency
- **GHG emissions transparency:** Scope 1/2/3 reporting and year-over-year trends
- **EV transition readiness:** Production targets, battery recycling, ICE phase-out timelines
- **Greenwashing detection:** Specificity of claims, supporting evidence, avoidance of excessive self-praise
- **Environmental compliance:** Water usage, hazardous waste, regulatory fines, supplier audits, product recalls and worker safety incidents
- **Overall readiness:** Comprehensive assessment for automotive industry transition

---

## Use Cases

### For Investors
- Compare sustainability performance across automakers
- Identify greenwashing vs genuine commitments
- Assess EV transition readiness
- Evaluate climate risk exposure

### For Analysts
- Benchmark automakers on standardized criteria
- Track progress over time (run annually)
- Identify disclosure gaps
- Generate comparable reports across companies

### For Sustainability Teams
- Understand best practices in automotive disclosure
- Identify areas for improvement
- Benchmark against competitors
- Prepare for investor scrutiny

---

## Running the Code

### Option 1: Web Interface (Recommended)

The web interface provides the most user-friendly experience with interactive visualizations.

**1. Start the application:**
```bash
streamlit run app.py
```

**2. What happens next:**
- Streamlit will start a local web server (usually on `http://localhost:8501`)
- Your default browser will automatically open
- You'll see the application interface

**3. Using the application:**

a) **Enter API Key** (in the app interface):
   - Paste your OpenAI API key in the password field
   - Click outside the field or press Enter

b) **Upload Reports**:
   - Drag and drop PDF files or click "Browse files"
   - Upload financial report (annual report, 10-K, etc.)
   - Upload sustainability report (ESG report, sustainability report, etc.)
   - You can upload one or both reports

c) **Analyze**:
   - Click "🔍 Analyze Reports" button
   - Processing typically takes 2-3 minutes
   - Progress indicators show: "📊 Analyzing financial report..." and "🌱 Analyzing sustainability report..."

d) **Review Results**:
   - **Scores section**: See financial score (0-16), sustainability score (0-17), and overall score (0-10)
   - **Breakdown section**: Detailed category scores with evidence
   - **Disclosure Quality Matrix**: Visual risk assessment (green = low risk, red = high risk)
   - **Investor Summary**: 1-page comprehensive analysis
   - **Raw Indicators**: Debug view with all extracted data

e) **Chat with Assistant** (right sidebar):
   - Ask questions about the analysis
   - Query the original documents
   - Get explanations for specific metrics

**Features:**
- ✅ No file paths to edit - upload directly
- ✅ Interactive visualizations
- ✅ Download investor summary as text file
- ✅ RAG-enabled chat assistant
- ✅ Session persistence (results stay until you refresh)

**Requirements:**
- OpenAI API key (entered in the app)
- Internet connection for OpenAI API calls
- Modern web browser (Chrome, Firefox, Safari, Edge)

**Processing time:**
- Financial analysis: ~60-90 seconds
- Sustainability analysis: ~60-90 seconds
- Summary generation: ~30 seconds
- **Total: 2-3 minutes** (varies based on PDF size and API response time)

#### AI Chat Assistant (RAG-Enabled)

After analysis is complete, the **chat assistant** automatically appears in the **right sidebar** where you can:

**Two modes of questioning:**

1. **Analysis questions** - Ask about the extracted scores and indicators:
   - "Why did the company score low on operating margin?"
   - "What are the biggest sustainability concerns?"
   - "How does the CapEx spending compare to healthy ranges?"

2. **Document search questions** - Ask questions that require retrieving from the original PDFs:
   - "What does the report say about supply chain risks?"
   - "Find mentions of lithium battery suppliers"
   - "Show me the company's future EV production plans"
   - "Does the report mention any regulatory violations?"

**How it works:**
- The assistant automatically detects when a question needs document retrieval (keywords like "report says", "find", "mention", "search")
- Uses RAG (Retrieval-Augmented Generation) to search the original PDF embeddings for relevant passages
- Combines extracted analysis data with retrieved document excerpts for comprehensive answers
- Maintains conversation history throughout your session
- **Sidebar design** keeps the investor summary and analysis visible in the main area while you ask questions

**Features:**
- ✅ Context-aware responses with specific numbers and evidence
- ✅ Conversation history tracking
- ✅ Access to both structured analysis AND raw document content
- ✅ Clear chat history button
- ✅ Sidebar design keeps analysis visible while chatting

---

### Option 2: Command Line Interface

The CLI version is useful for batch processing or scripting.

**1. Prepare your data:**
```bash
mkdir data
# Place your PDF files in the data/ folder
```

**2. Edit file paths in `main.py`** (lines 19-20):

The default paths are:
```python
FINANCIAL_PDF_PATH = os.path.join("data", "AAPL_2024_Annual_Report_Condensed.pdf")
SUSTAINABILITY_PDF_PATH = os.path.join("data", "RIVN_2024_Environmental_Metrics_Report.pdf")
```

Change these to your actual filenames:
```python
FINANCIAL_PDF_PATH = os.path.join("data", "your_financial_report.pdf")
SUSTAINABILITY_PDF_PATH = os.path.join("data", "your_sustainability_report.pdf")
```

**To skip an analysis**, set the path to `None`:
```python
FINANCIAL_PDF_PATH = None  # Skip financial analysis
SUSTAINABILITY_PDF_PATH = os.path.join("data", "sustainability_report.pdf")
```

**3. Run the script:**
```bash
python main.py
```

**4. What happens:**
- Console output shows progress: "Loading PDF...", "Building embeddings...", "Extracting indicators..."
- Results print to terminal with scores, breakdowns, and investor summary
- Processing time: 2-3 minutes

**Output format:**
```
Building vector store for financial report...
Split into 147 chunks. Building embeddings...
Vector store built.

Extracting financial indicators...
Financial score: 12 / 16 (normalized: 7.5 / 10)
  - Revenue Growth: 2 / 2
  - Gross Margin: 1 / 2
  ...

Sustainability score: 14 / 17 (normalized: 8.2 / 10)
  - GHG Emissions: 4 / 4
  ...

Overall score: 7.8 / 10

=== INVESTOR SUMMARY ===
[Full 1-page summary printed here]
```

**Advantages of CLI:**
- ✅ Faster for repeat analyses (no UI overhead)
- ✅ Can be scripted for batch processing
- ✅ Better for debugging (verbose console output)

**Disadvantages:**
- ❌ Must edit code to change files
- ❌ No interactive visualizations
- ❌ No chat assistant

---

## Reproducing Results

This section provides step-by-step instructions to reproduce the analysis results for the sample companies included in the project.

### Sample Data Included

The `data/` folder contains two sample PDF reports:

1. **Apple Inc. (AAPL) - 2024 Annual Report (Condensed)**
   - Financial report with income statement, balance sheet, and cash flow
   - Used for financial indicator extraction

2. **Rivian Automotive (RIVN) - 2024 Environmental Metrics Report**
   - Sustainability report with GHG emissions, EV targets, and environmental metrics
   - Used for sustainability indicator extraction

### Quick Start: Reproduce Sample Results

**Using Web Interface (Easiest):**

1. Ensure setup is complete (see Installation & Setup Guide below)
2. Run: `streamlit run app.py`
3. Enter your OpenAI API key in the interface
4. Upload `data/AAPL_2024_Annual_Report_Condensed.pdf` as financial report
5. Upload `data/RIVN_2024_Environmental_Metrics_Report.pdf` as sustainability report
6. Click "🔍 Analyze Reports"
7. Wait 2-3 minutes for processing

**Using CLI:**

1. Ensure setup is complete (see Installation & Setup Guide below)
2. Verify paths in `main.py` (lines 19-20) point to the sample files:
   ```python
   FINANCIAL_PDF_PATH = os.path.join("data", "AAPL_2024_Annual_Report_Condensed.pdf")
   SUSTAINABILITY_PDF_PATH = os.path.join("data", "RIVN_2024_Environmental_Metrics_Report.pdf")
   ```
3. Run: `python main.py`
4. Results will print to console

### Expected Results for Sample Data

**Apple (AAPL) Financial Score:**
- Expected range: 10-14 / 16 points
- Strong indicators: Revenue growth, R&D investment, inventory management
- Weaker indicators: Operating margins (depending on year)

**Rivian (RIVN) Sustainability Score:**
- Expected range: 12-16 / 17 points
- Strong indicators: EV targets (100% EV), GHG reporting, supply chain traceability
- Weaker indicators: May vary based on report completeness

**Overall Combined Score:**
- Expected range: 7.0-9.0 / 10

**Note:** Exact scores may vary slightly due to:
- OpenAI API model variations (temperature=0.0 reduces but doesn't eliminate variance)
- PDF parsing differences
- RAG retrieval variations (vector similarity is probabilistic)

### Reproducing with Your Own Data

**Step 1: Obtain PDF Reports**

For any automotive company, you need:

1. **Financial Report** (one of):
   - Annual report (10-K for US companies)
   - Quarterly report (10-Q)
   - Investor presentation with financial statements
   - **Must include**: Income statement, balance sheet, cash flow statement, MD&A

2. **Sustainability Report** (one of):
   - ESG report
   - Sustainability report
   - Environmental report
   - Corporate social responsibility (CSR) report
   - **Should include**: GHG emissions, environmental targets, compliance metrics

**Step 2: Prepare Files**

- Save PDFs to `data/` folder
- Use clear, descriptive filenames (e.g., `TSLA_2024_10K.pdf`, `TSLA_2024_ESG_Report.pdf`)
- Ensure PDFs are text-based (not scanned images)

**Step 3: Run Analysis**

Follow either "Option 1: Web Interface" or "Option 2: CLI" instructions above.

**Step 4: Interpret Results**

- **Financial Score (0-16)**: Higher is better; measures financial health
  - 13-16: Excellent
  - 9-12: Good
  - 5-8: Concerning
  - 0-4: Poor

- **Sustainability Score (0-17)**: Higher is better; measures disclosure quality
  - 14-17: Comprehensive disclosure
  - 10-13: Good disclosure with gaps
  - 6-9: Limited disclosure
  - 0-5: Minimal disclosure

- **Overall Score (0-10)**: Normalized average
  - 8.0-10.0: Strong performer
  - 6.0-7.9: Average performer
  - 4.0-5.9: Weak performer
  - 0.0-3.9: Very weak performer

### Validating Results

**Cross-Check Financial Indicators:**

Compare extracted metrics with actual reported figures:

1. **Revenue Growth**: Check MD&A section or investor presentation
2. **Margins**: Calculate manually from financial statements
   - Gross Margin = (Revenue - COGS) / Revenue
   - Operating Margin = Operating Income / Revenue
   - EBITDA Margin = EBITDA / Revenue
3. **CapEx %**: Capital expenditures / Revenue (from cash flow statement)
4. **R&D %**: R&D expense / Revenue (from income statement)
5. **DIO**: (Average Inventory / COGS) × 365 days

**Cross-Check Sustainability Indicators:**

Review sustainability report for:

1. **GHG Emissions**: Look for explicit Scope 1/2/3 figures (in tonnes CO2e)
2. **EV Targets**: Search for "EV production", "electrification", "battery electric vehicles"
3. **ICE Phase-out**: Look for "internal combustion", "gasoline", "diesel" phase-out dates
4. **Compliance**: Check for disclosures of fines, violations, recalls, incidents

**If Results Seem Incorrect:**

1. **Check PDF Quality**: Ensure text is extractable (try copying text from PDF)
2. **Review Evidence Fields**: Look at the raw indicators debug view
3. **Check Report Format**: Some reports may have non-standard layouts
4. **Verify Context Retrieval**: RAG may miss relevant sections if they use unusual terminology

### Batch Processing Multiple Companies

To analyze multiple companies efficiently:

**Method 1: CLI Loop (Python Script)**
```python
companies = [
    ("TSLA", "data/TSLA_2024_10K.pdf", "data/TSLA_2024_ESG.pdf"),
    ("GM", "data/GM_2024_10K.pdf", "data/GM_2024_ESG.pdf"),
    # Add more...
]

for name, financial, sustainability in companies:
    # Modify main.py paths programmatically
    # Run analysis
    # Save results to CSV/JSON
```

**Method 2: Web Interface (Manual)**
- Process each company one at a time
- Download investor summary for each
- Compile results in spreadsheet

### Cost Estimation

**OpenAI API Costs** (as of 2024, using gpt-4o-mini):

Per analysis:
- Embedding creation: ~$0.05-0.10 (depends on PDF size)
- LLM extraction calls: ~$0.10-0.20 (3 calls total)
- Summary generation: ~$0.05-0.10
- **Total per company: ~$0.20-0.40**

For 10 companies: ~$2-4
For 100 companies: ~$20-40

**Note**: Costs vary based on PDF length and model pricing. Check [OpenAI Pricing](https://openai.com/pricing) for current rates.

---

## Installation & Setup Guide

### Prerequisites

Before running the application, ensure you have:

- **Python 3.10 or higher** installed ([Download Python](https://www.python.org/downloads/))
- **OpenAI API key** ([Get your API key](https://platform.openai.com/api-keys))
- **Git** (optional, for cloning the repository)
- **Terminal/Command Prompt** access

### Step 1: Clone or Download the Repository

**Option A: Using Git**
```bash
git clone <repository-url>
cd CPSC-1710-Final-Project
```

**Option B: Download ZIP**
- Download the ZIP file from the repository
- Extract to a folder of your choice
- Open terminal/command prompt and navigate to the extracted folder

### Step 2: Create a Virtual Environment (Recommended)

Creating a virtual environment keeps dependencies isolated:

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the beginning of your command prompt when activated.

### Step 3: Install Dependencies

With the virtual environment activated, install all required packages:

```bash
pip install -r requirements.txt
```

**What gets installed:**
- `streamlit` - Web interface framework
- `langchain` and `langchain-community` - LLM orchestration
- `langchain-openai` - OpenAI integration
- `openai` - OpenAI API client
- `python-dotenv` - Environment variable management
- `pypdf` - PDF parsing
- `faiss-cpu` - Vector similarity search
- `tiktoken` - Token counting for OpenAI models

**Installation time:** ~2-3 minutes depending on internet speed.

### Step 4: Configure Environment Variables

Create a `.env` file in the project root directory:

**On Windows (Command Prompt):**
```bash
echo OPENAI_API_KEY=your_api_key_here > .env
```

**On macOS/Linux or Windows (PowerShell):**
```bash
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

**Or manually create the file:**
1. Create a new file named `.env` (no extension) in the project root
2. Add this line: `OPENAI_API_KEY=your_api_key_here`
3. Replace `your_api_key_here` with your actual OpenAI API key

**⚠️ Important:**
- Your API key should start with `sk-`
- Never commit the `.env` file to version control (it's in `.gitignore`)
- Keep your API key secure and private

### Step 5: Prepare Sample Data (For CLI Option)

If using the command-line interface (`main.py`), create a `data/` folder and add your PDF files:

```bash
mkdir data
```

Place your PDF files in this folder:
- `data/AAPL_2024_Annual_Report_Condensed.pdf` (or your financial report)
- `data/RIVN_2024_Environmental_Metrics_Report.pdf` (or your sustainability report)

**For the web interface (`app.py`)**, you can upload files directly through the browser interface.

### Step 6: Verify Installation

Test that everything is installed correctly:

```bash
python -c "import streamlit; import langchain; import openai; print('All dependencies installed successfully!')"
```

If you see "All dependencies installed successfully!", you're ready to go!

### Troubleshooting Common Issues

**Issue: `pip: command not found`**
- Try `pip3` instead of `pip`
- Or use `python -m pip install -r requirements.txt`

**Issue: `ModuleNotFoundError` after installation**
- Make sure your virtual environment is activated (you should see `(venv)` in terminal)
- Try reinstalling: `pip install --force-reinstall -r requirements.txt`

**Issue: `OPENAI_API_KEY not found` error**
- Verify `.env` file exists in project root directory
- Check that API key is on a line like: `OPENAI_API_KEY=sk-...`
- Ensure no spaces around the `=` sign
- Restart the application after creating `.env`

**Issue: SSL Certificate errors**
- On macOS: Run `/Applications/Python\ 3.x/Install\ Certificates.command`
- On Windows: Update pip: `python -m pip install --upgrade pip`

**Issue: FAISS installation fails**
- Try: `pip install faiss-cpu --no-cache-dir`
- On M1/M2 Mac: `pip install faiss-cpu --no-binary :all:`
