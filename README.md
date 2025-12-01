# CPSC-1710-Final-Project
Financial/Sustainability Analysis Tool for Introduction to AI Applications

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
- 1: Gross margin is positive but flat or declined
- 0: Gross margin is negative

**Why this matters:** Improving gross margins demonstrate pricing power and manufacturing efficiency, critical as EV production scales and battery costs decline.

---

#### 3. Operating Margin (2 points)
- 2: Operating margin is positive AND improved year-over-year
- 1: Operating margin is positive but flat or declined
- 0: Operating margin is negative

**Why this matters:** Operating margin improvement shows effective cost management during the capital-intensive EV transition period.

---

#### 4. EBITDA Margin (2 points)
- 2: EBITDA margin is positive AND improved year-over-year
- 1: EBITDA margin is positive but flat or declined
- 0: EBITDA margin is negative

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

### Sustainability Indicators (15 points → normalized to 10)

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

#### 4. Environmental & Compliance Metrics (4 points)
- ✓ Water usage metrics disclosed
- ✓ Hazardous waste metrics disclosed
- ✓ Regulatory fines/violations disclosed
- ✓ Supplier audit frequency mentioned

**Why this matters:** These operational metrics reveal environmental management maturity and regulatory compliance beyond just carbon emissions.

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
3. **Quality & Compliance Query** – sustainability claims, water usage, hazardous waste, regulatory fines, supplier audits  

All retrieved contexts are combined before analysis so the LLM has the relevant evidence for all **15 sustainability criteria**.


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

Sustainability score: Z / 15 (normalized: W / 10)
  - GHG Emissions: I / 4
  - Automotive Targets: J / 4
  - Transparency: K / 3
  - Environmental/Compliance: L / 4

Overall score: M / 10
```

### Investor Summary
Tailored to automotive industry with focus on:
- **Financial health:** Revenue growth, profitability margins (gross, operating, EBITDA), cash flow generation, capital allocation (CapEx, R&D), and inventory efficiency
- **GHG emissions transparency:** Scope 1/2/3 reporting and year-over-year trends
- **EV transition readiness:** Production targets, battery recycling, ICE phase-out timelines
- **Greenwashing detection:** Specificity of claims, supporting evidence, avoidance of excessive self-praise
- **Environmental compliance:** Water usage, hazardous waste, regulatory fines, supplier audits
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

## Running the Tool

### Option 1: Web Interface (Recommended)

Run the interactive web application:

```bash
streamlit run app.py
```

This will open a web interface in your browser where you can:
- Upload financial and/or sustainability reports via drag-and-drop
- View interactive scores and breakdowns (Financial: 0-16 points, Sustainability: 0-15 points)
- See a visual disclosure quality matrix showing greenwashing risk
- Download the investor summary as a text file
- See detailed raw indicators for debugging

**Requirements:**
- OpenAI API key in `.env` file
- Internet connection for OpenAI API calls

**Processing time:** ~2-3 minutes depending on document size and API response time.

---

### Option 2: Command Line Interface

Run the traditional CLI version:

```bash
python main.py
```

Edit the paths in `main.py` to point to your PDF files:
```python
FINANCIAL_PDF_PATH = "path/to/financial_report.pdf"
SUSTAINABILITY_PDF_PATH = "path/to/sustainability_report.pdf"
```

Set either path to `None` to skip that analysis.

---

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```
