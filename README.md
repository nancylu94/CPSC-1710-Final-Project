# CPSC-1710-Final-Project
Financial/Sustainability Analysis Tool for Introduction to AI Applications

FINANCIAL CRITERIA


# Automotive-Specific Sustainability Criteria

## Overview
This tool has been customized to assess **automotive manufacturers** specifically, with sustainability criteria tailored to the EV transition and automotive industry challenges.

## Scoring Structure

### Financial Indicators (5 points → normalized to 10)
Unchanged from original:
- Revenue growth (YoY)
- Margin stability/improvement
- Free cash flow/operating cash flow
- Leverage trends
- Forward guidance

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

### Multi-Pass RAG Retrieval
The tool uses **3 separate retrieval queries** to ensure comprehensive coverage:

1. **GHG Query:** Retrieves chunks about Scope 1/2/3 emissions and YoY changes
2. **Automotive Query:** Retrieves chunks about EVs, batteries, ICE phase-out, supply chain
3. **Quality/Compliance Query:** Retrieves chunks about sustainability claims, water, waste, fines, audits

All contexts are combined before analysis to ensure the LLM has relevant information for all 15 criteria.

---

## Output Format

### Scores Display
```
Financial score: X / 5 (normalized: Y / 10)
Sustainability score: Z / 15 (normalized: W / 10)
  - GHG Emissions: A / 4
  - Automotive Targets: B / 4
  - Transparency: C / 3
  - Environmental/Compliance: D / 4
Overall score: E / 10
```

### Investor Summary
Tailored to automotive industry with focus on:
- Financial health
- GHG emissions transparency
- EV transition readiness
- Greenwashing detection
- Environmental compliance
- Overall readiness for automotive industry transition

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

```bash
python main.py
```

**Requirements:**
- Annual financial report PDF
- Sustainability/Impact report PDF
- OpenAI API key in `.env` file

**Processing time:** ~2-3 minutes depending on document size and API response time.
