# Financial Indicators - Sophisticated Scoring System

## Overview
Financial indicators use a **0-2 point scoring system** for each metric, allowing for nuanced assessment beyond simple yes/no.

**Maximum Score: 16 points** (8 indicators × 2 points each)

---

## Scoring Breakdown

### 1. YoY Revenue Growth (0-2 points)

**Scoring:**
- **2 points**: Revenue increased >5% year-over-year
- **1 point**: Revenue increased 0-5% year-over-year
- **0 points**: Revenue declined year-over-year or flat/negative
- **null**: Not enough information to determine YoY change

**Rationale:** Strong growth (>5%) is rewarded. Modest growth still gets credit. Decline is concerning.

---

### 2. Gross Margin (0-2 points)

**Scoring:**
- **2 points**: Gross margin is positive AND clearly higher than previous year
- **1 point**: Gross margin is positive but NOT clearly higher (flat, lower, or no YoY info)
- **0 points**: Gross margin is negative
- **null**: Cannot determine gross margin level

**Rationale:** Positive margins are essential for automakers. Improvement shows operational efficiency gains.

---

### 3. Operating Margin (0-2 points)

**Scoring:**
- **2 points**: Operating margin is positive AND clearly higher than previous year
- **1 point**: Operating margin is positive but NOT clearly higher
- **0 points**: Operating margin is negative
- **null**: Cannot determine operating margin

**Rationale:** Operating profitability demonstrates ability to cover all operating expenses.

---

### 4. EBITDA Margin (0-2 points)

**Scoring:**
- **2 points**: EBITDA margin is positive AND clearly higher than previous year
- **1 point**: EBITDA margin is positive but NOT clearly higher
- **0 points**: EBITDA margin is negative
- **null**: Cannot determine EBITDA margin

**Rationale:** EBITDA shows core operational cash generation before financing decisions.

---

### 5. Free Cash Flow (0-2 points)

**Scoring:**
- **2 points**: FCF is clearly positive
- **1 point**: FCF is around break-even (0 to -5% of revenue, or described as approximately breakeven)
- **0 points**: FCF is clearly negative and worse than -5% of revenue
- **null**: Not enough information to determine FCF

**Rationale:** Positive FCF indicates sustainable business. Near-breakeven is acceptable for growth companies.

---

### 6. CapEx as % of Revenue (0-2 points)

**Scoring:**
- **2 points**: CapEx is 3-8% of revenue (healthy range)
- **1 point**: CapEx is 8-12% of revenue (aggressive but acceptable)
- **0 points**: CapEx is <3% (under-investing) OR >12% (very heavy spending)
- **null**: Cannot estimate CapEx as % of revenue

**Rationale:** Balance is key. Too low suggests under-investment in growth/capacity. Too high may indicate inefficiency or unsustainable expansion.

---

### 7. R&D as % of Revenue (0-2 points)

**Scoring:**
- **2 points**: R&D is 4-10% of revenue
- **1 point**: R&D is 2-4% of revenue (minimal but acceptable)
- **0 points**: R&D is <2% (under-investing) OR >10% (very high)
- **null**: Cannot estimate R&D as % of revenue

**Rationale:** Automotive sector requires significant R&D for EV transition, autonomy, and competitiveness. 4-10% is industry-appropriate.

---

### 8. Inventory & Days Inventory Outstanding (0-2 points)

**Scoring:**
- **2 points**: DIO <40 days OR inventory described as lean/tightly managed
- **1 point**: DIO 40-70 days OR inventory described as normal/acceptable
- **0 points**: DIO >70 days OR inventory clearly elevated/excess
- **null**: No DIO or meaningful inventory information

**Rationale:** Lower DIO indicates efficient operations and strong demand. High DIO suggests weak demand or production inefficiencies.

---

## Interpretation Guide

### Excellent Financial Health (13-16 points)
- Strong revenue growth
- Improving margins across the board
- Positive FCF
- Healthy investment in both CapEx and R&D
- Efficient inventory management

### Good Financial Health (9-12 points)
- Moderate revenue growth
- Positive margins (may not be improving)
- Near-breakeven or positive FCF
- Reasonable CapEx/R&D levels
- Acceptable inventory levels

### Concerning Financial Health (5-8 points)
- Weak or negative revenue growth
- Some negative margins
- Negative FCF
- Imbalanced CapEx or R&D spending
- Inventory issues

### Poor Financial Health (0-4 points)
- Revenue decline
- Multiple negative margins
- Significant cash burn
- Under-investment or over-investment
- Major inventory problems

---

## Key Differences from Previous Version

**Old System:**
- Simple boolean (true/false) for 5 indicators
- Maximum score: 5 points
- Less granularity

**New System:**
- 0-2 point scale for 8 indicators
- Maximum score: 16 points
- More sophisticated assessment
- Allows for "partially good" situations (1 point)
- Handles missing data explicitly (null)
- Industry-specific thresholds (CapEx, R&D, DIO)

---

## Why This Matters for Automakers

1. **Capital Intensity**: Automakers require significant CapEx for manufacturing. The 3-12% range reflects industry norms.

2. **R&D for EV Transition**: 4-10% R&D spend is critical for developing competitive EVs, batteries, and autonomous tech.

3. **Inventory Management**: In automotive, DIO is crucial. High inventory can indicate demand issues or production/supply chain problems.

4. **Margin Improvement**: The focus on YoY improvement rewards companies making progress in the difficult transition to EVs.

5. **Cash Flow Reality**: FCF breakeven tolerance (-5% to 0%) acknowledges that growth-stage EV companies may not yet be FCF positive.
