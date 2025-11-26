import os
import json
from dataclasses import dataclass
from typing import Dict, Any

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate

# --------- CONFIG: PDF paths and model name ---------

# Set to None to skip analysis
FINANCIAL_PDF_PATH = "C:/Users/nancy/OneDrive - Yale University/Documents/1. School/4. Yale MAM/3. Academics/MGT 695/CPSC-1710-Final-Project/data/AAPL_2024_Annual_Report_Condensed.pdf"
SUSTAINABILITY_PDF_PATH = "C:/Users/nancy/OneDrive - Yale University/Documents/1. School/4. Yale MAM/3. Academics/MGT 695/CPSC-1710-Final-Project/data/RIVN_2024_Environmental_Metrics_Report.pdf"

MODEL_NAME = "gpt-4o-mini"  # option to switch to gpt-4o (more expensive)

if "OPENAI_API_KEY" not in os.environ:
    raise RuntimeError(
        "OPENAI_API_KEY not found. Make sure you created a .env file with OPENAI_API_KEY=your_key"
    )

# --------- DATA CLASSES ---------

# Financial indicators with numeric scoring (0, 1, 2, or null)
@dataclass
class FinancialIndicators:
    # 1) Revenue Growth
    revenue_growth_score: int | None  # 0, 1, 2, or None
    revenue_growth_evidence: str

    # 2) Gross Margin
    gross_margin_score: int | None
    gross_margin_evidence: str

    # 3) Operating Margin
    operating_margin_score: int | None
    operating_margin_evidence: str

    # 4) EBITDA Margin
    ebitda_margin_score: int | None
    ebitda_margin_evidence: str

    # 5) Free Cash Flow
    fcf_score: int | None
    fcf_evidence: str

    # 6) CapEx as % of Revenue
    capex_score: int | None
    capex_evidence: str

    # 7) R&D as % of Revenue
    rnd_score: int | None
    rnd_evidence: str

    # 8) Inventory & Days Inventory Outstanding
    inventory_score: int | None
    inventory_evidence: str


# Sustainability/ESG indicators specifically for automotive manufacturers
@dataclass
class SustainabilityIndicators:
    # 1) GHG Emissions with YoY changes
    ghg_scope1_reported: bool
    ghg_scope1_evidence: str
    ghg_scope2_reported: bool
    ghg_scope2_evidence: str
    ghg_scope3_reported: bool
    ghg_scope3_evidence: str
    ghg_yoy_change_reported: bool
    ghg_yoy_evidence: str

    # 2) Automotive-specific targets and progress
    ev_production_targets: bool
    ev_targets_evidence: str
    battery_recycling_reported: bool
    battery_recycling_evidence: str
    ice_phaseout_date_specified: bool
    ice_phaseout_evidence: str
    supply_chain_traceability: bool
    supply_chain_evidence: str

    # 3) Greenwashing indicators (higher score = less greenwashing)
    claims_have_specificity: bool  # Dates, numbers, not vague
    specificity_evidence: str
    claims_have_supporting_evidence: bool
    supporting_evidence: str
    avoids_excessive_self_praise: bool
    self_praise_evidence: str

    # 4) Environmental & compliance metrics
    water_usage_reported: bool
    water_usage_evidence: str
    hazardous_waste_reported: bool
    hazardous_waste_evidence: str
    regulatory_fines_disclosed: bool
    fines_evidence: str
    supplier_audit_frequency: bool
    audit_evidence: str


# --------- RAG HELPERS ---------

def build_vectorstore_from_pdf(pdf_path: str) -> FAISS:
    """Load a PDF, chunk it, embed the chunks, and store in FAISS."""
    print(f"Loading PDF: {pdf_path}")
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=200,
    )
    docs = splitter.split_documents(documents)

    print(f"Split into {len(docs)} chunks. Building embeddings...")

    # Create an embeddings model
    embeddings = OpenAIEmbeddings()

    # Build FAISS vector store
    vs = FAISS.from_documents(docs, embeddings)
    print("Vector store built.")
    return vs


def retrieve_context(question: str, vectorstore: FAISS, k: int = 8) -> str:
    """Retrieve top-k chunks for a question and join them into one context string."""
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    docs = retriever.invoke(question)

    parts = []
    for i, d in enumerate(docs, start=1):
        parts.append(f"### CHUNK {i}\n{d.page_content}")

    return "\n\n".join(parts)


def get_llm() -> ChatOpenAI:
    """Create a deterministic ChatOpenAI client for extraction & summaries."""
    return ChatOpenAI(model=MODEL_NAME, temperature=0.0)


# --------- EXTRACTION FUNCTIONS ---------

def extract_financial_indicators(llm: ChatOpenAI, vs: FAISS) -> FinancialIndicators:
    question = (
        "Information about revenue growth, gross margin, operating margin, EBITDA margin, "
        "free cash flow, capital expenditures, R&D spending, inventory, and days inventory outstanding"
    )

    context = retrieve_context(question, vs, k=10)

    prompt = ChatPromptTemplate.from_template(
        """
You are a financial analyst reading a company's annual report.

CONTEXT:
{context}

For each indicator below, you will:
1) Determine the underlying facts from the CONTEXT
2) Assign a numeric score (0, 1, or 2) using the rules below
3) Provide brief evidence referencing specific numbers from the CONTEXT

If required information is not stated or cannot be reliably inferred, set the score to null.

**1) YoY Revenue Growth (revenue_growth_score)**
Determine if revenue increased compared to prior period.

Scoring:
- 2: Revenue increased >5% year-over-year
- 1: Revenue increased 0-5% year-over-year
- 0: Revenue declined year-over-year or flat/negative
- null: Not enough information to determine YoY change

**2) Gross Margin (gross_margin_score)**
Focus on overall or automotive gross margin. Check if positive (>0%) and if improved YoY.

Scoring:
- 2: Gross margin is positive AND clearly higher than previous year
- 1: Gross margin is positive but NOT clearly higher (flat, lower, or no YoY info)
- 0: Gross margin is negative
- null: Cannot determine gross margin level

**3) Operating Margin (operating_margin_score)**
Use operating margin or EBIT margin. Check if positive and improved YoY.

Scoring:
- 2: Operating margin is positive AND clearly higher than previous year
- 1: Operating margin is positive but NOT clearly higher
- 0: Operating margin is negative
- null: Cannot determine operating margin

**4) EBITDA Margin (ebitda_margin_score)**
Check if EBITDA margin is positive and improved YoY.

Scoring:
- 2: EBITDA margin is positive AND clearly higher than previous year
- 1: EBITDA margin is positive but NOT clearly higher
- 0: EBITDA margin is negative
- null: Cannot determine EBITDA margin

**5) Free Cash Flow (fcf_score)**
Use free cash flow (FCF) as defined in report.

Scoring:
- 2: FCF is clearly positive
- 1: FCF is around break-even (0 to -5% of revenue, or described as approximately breakeven)
- 0: FCF is clearly negative and worse than -5% of revenue
- null: Not enough information to determine FCF

**6) CapEx as % of Revenue (capex_score)**
Use capital expenditures or PP&E purchases. Estimate % if both CapEx and revenue given.

Scoring:
- 2: CapEx is 3-8% of revenue (healthy range)
- 1: CapEx is 8-12% of revenue (aggressive but acceptable)
- 0: CapEx is <3% (under-investing) OR >12% (very heavy spending)
- null: Cannot estimate CapEx as % of revenue

**7) R&D as % of Revenue (rnd_score)**
Use R&D expense divided by revenue.

Scoring:
- 2: R&D is 4-10% of revenue
- 1: R&D is 2-4% of revenue (minimal but acceptable)
- 0: R&D is <2% (under-investing) OR >10% (very high)
- null: Cannot estimate R&D as % of revenue

**8) Inventory & Days Inventory Outstanding (inventory_score)**
Use DIO if provided, or qualitative commentary on inventory trends.

Scoring:
- 2: DIO <40 days OR inventory described as lean/tightly managed
- 1: DIO 40-70 days OR inventory described as normal/acceptable
- 0: DIO >70 days OR inventory clearly elevated/excess
- null: No DIO or meaningful inventory information

Return a STRICT JSON object with these exact keys:

{{
  "revenue_growth_score": 0 or 1 or 2 or null,
  "revenue_growth_evidence": "string with specific numbers/percentages",
  "gross_margin_score": 0 or 1 or 2 or null,
  "gross_margin_evidence": "string",
  "operating_margin_score": 0 or 1 or 2 or null,
  "operating_margin_evidence": "string",
  "ebitda_margin_score": 0 or 1 or 2 or null,
  "ebitda_margin_evidence": "string",
  "fcf_score": 0 or 1 or 2 or null,
  "fcf_evidence": "string",
  "capex_score": 0 or 1 or 2 or null,
  "capex_evidence": "string",
  "rnd_score": 0 or 1 or 2 or null,
  "rnd_evidence": "string",
  "inventory_score": 0 or 1 or 2 or null,
  "inventory_evidence": "string"
}}

ONLY output the JSON object, no extra text.
        """
    )

    chain = prompt | llm
    resp = chain.invoke({"context": context})
    data: Dict[str, Any] = json.loads(resp.content)

    return FinancialIndicators(
        revenue_growth_score=data["revenue_growth_score"],
        revenue_growth_evidence=data["revenue_growth_evidence"],
        gross_margin_score=data["gross_margin_score"],
        gross_margin_evidence=data["gross_margin_evidence"],
        operating_margin_score=data["operating_margin_score"],
        operating_margin_evidence=data["operating_margin_evidence"],
        ebitda_margin_score=data["ebitda_margin_score"],
        ebitda_margin_evidence=data["ebitda_margin_evidence"],
        fcf_score=data["fcf_score"],
        fcf_evidence=data["fcf_evidence"],
        capex_score=data["capex_score"],
        capex_evidence=data["capex_evidence"],
        rnd_score=data["rnd_score"],
        rnd_evidence=data["rnd_evidence"],
        inventory_score=data["inventory_score"],
        inventory_evidence=data["inventory_evidence"],
    )


def extract_sustainability_indicators(llm: ChatOpenAI, vs: FAISS) -> SustainabilityIndicators:
    # Multiple retrieval passes for different aspects

    # Query 1: GHG emissions
    ghg_context = retrieve_context(
        "Scope 1, Scope 2, and Scope 3 greenhouse gas emissions with numeric values and year-on-year changes",
        vs, k=8
    )

    # Query 2: Automotive targets
    auto_context = retrieve_context(
        "EV production percentages, battery recycling rates, ICE phase-out dates, supply chain traceability",
        vs, k=8
    )

    # Query 3: Greenwashing and compliance
    quality_context = retrieve_context(
        "Sustainability claims, net-zero commitments, water usage, hazardous waste, regulatory fines, supplier audits",
        vs, k=8
    )

    # Combine all contexts
    combined_context = f"{ghg_context}\n\n{auto_context}\n\n{quality_context}"

    prompt = ChatPromptTemplate.from_template(
        """
You are an ESG analyst specializing in automotive industry sustainability reporting.

CONTEXT:
{context}

Return a STRICT JSON object with exactly these keys and types:

**1) GHG EMISSIONS & YoY CHANGES:**
- ghg_scope1_reported: true if Scope 1 emissions reported with numeric values
- ghg_scope1_evidence: string (include actual numbers if available)
- ghg_scope2_reported: true if Scope 2 emissions reported with numeric values
- ghg_scope2_evidence: string (include actual numbers if available)
- ghg_scope3_reported: true if Scope 3 emissions reported with numeric values
- ghg_scope3_evidence: string (include actual numbers if available)
- ghg_yoy_change_reported: true if year-on-year changes are shown
- ghg_yoy_evidence: string (include percentage changes or trends)

**2) AUTOMOTIVE-SPECIFIC TARGETS:**
- ev_production_targets: true if EV production percentages or targets are specified
- ev_targets_evidence: string (e.g., "Target 50% EV sales by 2030")
- battery_recycling_reported: true if battery recycling rates or programs are mentioned
- battery_recycling_evidence: string
- ice_phaseout_date_specified: true if phase-out date for ICE vehicles is provided
- ice_phaseout_evidence: string
- supply_chain_traceability: true if supply chain tracking/auditing is documented
- supply_chain_evidence: string

**3) GREENWASHING INDICATORS (assess quality of claims):**
- claims_have_specificity: true if sustainability claims include dates, numbers, timelines (NOT vague like "committed to," "striving," "leading")
- specificity_evidence: string (quote specific vs vague claims)
- claims_have_supporting_evidence: true if claims are backed by data, third-party verification, or concrete metrics
- supporting_evidence: string
- avoids_excessive_self_praise: true if language is factual vs promotional ("world-leading," "pioneering," etc.)
- self_praise_evidence: string (quote excessive self-praise if found)

**4) ENVIRONMENTAL & COMPLIANCE METRICS:**
- water_usage_reported: true if water usage metrics are disclosed
- water_usage_evidence: string
- hazardous_waste_reported: true if hazardous waste metrics are disclosed
- hazardous_waste_evidence: string
- regulatory_fines_disclosed: true if environmental fines or violations are disclosed
- fines_evidence: string
- supplier_audit_frequency: true if supplier audit frequency is mentioned
- audit_evidence: string

The output MUST be valid JSON with all 24 fields. For example:

{{
  "ghg_scope1_reported": true,
  "ghg_scope1_evidence": "...",
  ...
}}

If information is not found, set boolean to false and explain in evidence field.

ONLY output the JSON object, no extra text.
        """
    )

    chain = prompt | llm
    resp = chain.invoke({"context": combined_context})
    data: Dict[str, Any] = json.loads(resp.content)

    return SustainabilityIndicators(
        ghg_scope1_reported=data["ghg_scope1_reported"],
        ghg_scope1_evidence=data["ghg_scope1_evidence"],
        ghg_scope2_reported=data["ghg_scope2_reported"],
        ghg_scope2_evidence=data["ghg_scope2_evidence"],
        ghg_scope3_reported=data["ghg_scope3_reported"],
        ghg_scope3_evidence=data["ghg_scope3_evidence"],
        ghg_yoy_change_reported=data["ghg_yoy_change_reported"],
        ghg_yoy_evidence=data["ghg_yoy_evidence"],
        ev_production_targets=data["ev_production_targets"],
        ev_targets_evidence=data["ev_targets_evidence"],
        battery_recycling_reported=data["battery_recycling_reported"],
        battery_recycling_evidence=data["battery_recycling_evidence"],
        ice_phaseout_date_specified=data["ice_phaseout_date_specified"],
        ice_phaseout_evidence=data["ice_phaseout_evidence"],
        supply_chain_traceability=data["supply_chain_traceability"],
        supply_chain_evidence=data["supply_chain_evidence"],
        claims_have_specificity=data["claims_have_specificity"],
        specificity_evidence=data["specificity_evidence"],
        claims_have_supporting_evidence=data["claims_have_supporting_evidence"],
        supporting_evidence=data["supporting_evidence"],
        avoids_excessive_self_praise=data["avoids_excessive_self_praise"],
        self_praise_evidence=data["self_praise_evidence"],
        water_usage_reported=data["water_usage_reported"],
        water_usage_evidence=data["water_usage_evidence"],
        hazardous_waste_reported=data["hazardous_waste_reported"],
        hazardous_waste_evidence=data["hazardous_waste_evidence"],
        regulatory_fines_disclosed=data["regulatory_fines_disclosed"],
        fines_evidence=data["fines_evidence"],
        supplier_audit_frequency=data["supplier_audit_frequency"],
        audit_evidence=data["audit_evidence"],
    )


# --------- SCORING ---------

def compute_financial_score(fi: FinancialIndicators) -> int:
    """
    Sum all financial indicator scores.
    Each indicator can score 0, 1, or 2 points (or None).
    Maximum possible: 16 points (8 indicators × 2 points each)
    """
    score = 0

    # Sum up all non-None scores
    if fi.revenue_growth_score is not None:
        score += fi.revenue_growth_score
    if fi.gross_margin_score is not None:
        score += fi.gross_margin_score
    if fi.operating_margin_score is not None:
        score += fi.operating_margin_score
    if fi.ebitda_margin_score is not None:
        score += fi.ebitda_margin_score
    if fi.fcf_score is not None:
        score += fi.fcf_score
    if fi.capex_score is not None:
        score += fi.capex_score
    if fi.rnd_score is not None:
        score += fi.rnd_score
    if fi.inventory_score is not None:
        score += fi.inventory_score

    return score  # Out of 16 total


def compute_sustainability_score(si: SustainabilityIndicators) -> int:
    """
    Score out of 20 points across 4 categories for automotive sustainability.

    Category 1: GHG Emissions Reporting (4 points)
    Category 2: Automotive Targets & Progress (4 points)
    Category 3: Transparency & Anti-Greenwashing (3 points)
    Category 4: Environmental & Compliance (4 points)

    Total: 15 points, normalized to 0-10 scale for reporting
    """
    score = 0

    # Category 1: GHG Emissions (4 points)
    if si.ghg_scope1_reported:
        score += 1
    if si.ghg_scope2_reported:
        score += 1
    if si.ghg_scope3_reported:
        score += 1
    if si.ghg_yoy_change_reported:
        score += 1

    # Category 2: Automotive Targets (4 points)
    if si.ev_production_targets:
        score += 1
    if si.battery_recycling_reported:
        score += 1
    if si.ice_phaseout_date_specified:
        score += 1
    if si.supply_chain_traceability:
        score += 1

    # Category 3: Transparency/Anti-Greenwashing (3 points)
    if si.claims_have_specificity:
        score += 1
    if si.claims_have_supporting_evidence:
        score += 1
    if si.avoids_excessive_self_praise:
        score += 1

    # Category 4: Environmental & Compliance (4 points)
    if si.water_usage_reported:
        score += 1
    if si.hazardous_waste_reported:
        score += 1
    if si.regulatory_fines_disclosed:
        score += 1
    if si.supplier_audit_frequency:
        score += 1

    return score  # Out of 15 total


# --------- SUMMARY GENERATION ---------

def generate_summary(
    llm: ChatOpenAI,
    f_score: int,
    s_score: int,
    fi: FinancialIndicators,
    si: SustainabilityIndicators,
) -> str:
    """
    Generate a comprehensive 1-page investor summary with:
    - Executive overview
    - Financial analysis with bullet points and supporting evidence
    - Sustainability analysis with bullet points and supporting evidence
    - Pros and Cons
    - Risk factors
    """

    # Normalize scores for comparison (both on 0-10 scale)
    f_score_normalized = (f_score / 16) * 10  # Financial max is now 16
    s_score_normalized = (s_score / 15) * 10
    overall = (f_score_normalized + s_score_normalized) / 2

    payload = {
        "financial_score": f_score,
        "financial_score_out_of": 16,
        "financial_score_normalized": f_score_normalized,
        "sustainability_score": s_score,
        "sustainability_score_out_of": 15,
        "sustainability_score_normalized": s_score_normalized,
        "overall_score": overall,
        "financial_indicators": fi.__dict__,
        "sustainability_indicators": si.__dict__,
    }

    prompt = ChatPromptTemplate.from_template(
        """
You are writing a comprehensive 1-page investor report for an AUTOMOTIVE company.

Here are structured scores and evidence:
{payload_json}

Generate a well-structured report with the following sections:

## EXECUTIVE OVERVIEW
2-3 sentences summarizing the company's overall financial health (score: {f_score}/16) and sustainability performance (score: {s_score}/15).

## FINANCIAL ANALYSIS (Score: {f_score}/16, Normalized: {f_norm:.1f}/10)
Provide 4-6 bullet points analyzing:
- Revenue growth trends with specific percentages/figures from evidence
- Profitability metrics (gross, operating, EBITDA margins) with YoY changes
- Cash flow position and capital allocation (FCF, CapEx, R&D as % of revenue)
- Operational efficiency (inventory management)

For each bullet point, include supporting snippets from the evidence fields (actual numbers, percentages, or quotes).

## SUSTAINABILITY ANALYSIS (Score: {s_score}/15, Normalized: {s_norm:.1f}/10)
Provide 4-6 bullet points analyzing:
- GHG emissions reporting (Scope 1/2/3 coverage and YoY trends)
- EV transition strategy (production targets, ICE phase-out, battery recycling)
- Transparency and greenwashing assessment (specificity of claims, third-party verification)
- Environmental compliance (water, waste, fines, supplier audits)

For each bullet point, include supporting snippets from the evidence fields (actual emissions data, target dates, certifications).

## STRENGTHS
List 3-4 key competitive advantages or positive indicators based on the data.

## WEAKNESSES
List 3-4 areas of concern, gaps in disclosure, or negative trends.

## RISK FACTORS
Identify 3-4 material risks based on the financial and sustainability analysis:
- Financial risks (cash burn, margin pressure, inventory issues, etc.)
- Transition risks (EV adoption delays, regulatory changes, etc.)
- ESG risks (emissions trajectory, greenwashing exposure, compliance issues, etc.)

## INVESTMENT RECOMMENDATION
1-2 sentences with overall assessment and readiness for automotive industry transition.

Keep the entire report under 600 words. Use clear, professional language. Quote specific numbers from evidence fields.
        """
    )

    chain = prompt | llm
    resp = chain.invoke({
        "payload_json": json.dumps(payload, indent=2),
        "f_score": f_score,
        "s_score": s_score,
        "f_norm": f_score_normalized,
        "s_norm": s_score_normalized
    })
    return resp.content.strip()


# --------- MAIN ---------

def main():
    # 1) Build vector store for financial report (if provided)
    fi = None
    f_score = 0
    f_score_normalized = 0

    if FINANCIAL_PDF_PATH:
        financial_vs = build_vectorstore_from_pdf(FINANCIAL_PDF_PATH)
        llm = get_llm()
        print("\nExtracting financial indicators...")
        fi = extract_financial_indicators(llm, financial_vs)
        f_score = compute_financial_score(fi)
        f_score_normalized = (f_score / 16) * 10
    else:
        print("\n[Skipping financial analysis - no financial report provided]")

    # 2) Build vector store for sustainability report (if provided)
    si = None
    s_score = 0
    s_score_normalized = 0

    if SUSTAINABILITY_PDF_PATH:
        sustainability_vs = build_vectorstore_from_pdf(SUSTAINABILITY_PDF_PATH)
        llm = get_llm()
        print("\nExtracting sustainability indicators...")
        si = extract_sustainability_indicators(llm, sustainability_vs)
        s_score = compute_sustainability_score(si)
        s_score_normalized = (s_score / 15) * 10
    else:
        print("\n[Skipping sustainability analysis - no sustainability report provided]")

    # Calculate overall score
    if FINANCIAL_PDF_PATH and SUSTAINABILITY_PDF_PATH:
        overall = (f_score_normalized + s_score_normalized) / 2
    elif FINANCIAL_PDF_PATH:
        overall = f_score_normalized
    elif SUSTAINABILITY_PDF_PATH:
        overall = s_score_normalized
    else:
        overall = 0
        print("\n[ERROR: No reports provided for analysis]")

    # 6) Print raw indicators (debug)
    print("\n--- RAW INDICATORS ---")
    if fi:
        print("FINANCIAL:")
        print(fi)
        print("\n")
    if si:
        print("SUSTAINABILITY:")
        print(si)

    # 7) Print scores
    print("\n--- SCORES ---")
    if FINANCIAL_PDF_PATH and fi:
        print(f"Financial score: {f_score} / 16 (normalized: {f_score_normalized:.1f} / 10)")
        print(f"  - Revenue Growth: {fi.revenue_growth_score if fi.revenue_growth_score is not None else 'N/A'} / 2")
        print(f"  - Gross Margin: {fi.gross_margin_score if fi.gross_margin_score is not None else 'N/A'} / 2")
        print(f"  - Operating Margin: {fi.operating_margin_score if fi.operating_margin_score is not None else 'N/A'} / 2")
        print(f"  - EBITDA Margin: {fi.ebitda_margin_score if fi.ebitda_margin_score is not None else 'N/A'} / 2")
        print(f"  - Free Cash Flow: {fi.fcf_score if fi.fcf_score is not None else 'N/A'} / 2")
        print(f"  - CapEx % of Revenue: {fi.capex_score if fi.capex_score is not None else 'N/A'} / 2")
        print(f"  - R&D % of Revenue: {fi.rnd_score if fi.rnd_score is not None else 'N/A'} / 2")
        print(f"  - Inventory/DIO: {fi.inventory_score if fi.inventory_score is not None else 'N/A'} / 2")
    if SUSTAINABILITY_PDF_PATH and si:
        print(f"Sustainability score: {s_score} / 15 (normalized: {s_score_normalized:.1f} / 10)")
        print(f"  - GHG Emissions: {sum([si.ghg_scope1_reported, si.ghg_scope2_reported, si.ghg_scope3_reported, si.ghg_yoy_change_reported])} / 4")
        print(f"  - Automotive Targets: {sum([si.ev_production_targets, si.battery_recycling_reported, si.ice_phaseout_date_specified, si.supply_chain_traceability])} / 4")
        print(f"  - Transparency: {sum([si.claims_have_specificity, si.claims_have_supporting_evidence, si.avoids_excessive_self_praise])} / 3")
        print(f"  - Environmental/Compliance: {sum([si.water_usage_reported, si.hazardous_waste_reported, si.regulatory_fines_disclosed, si.supplier_audit_frequency])} / 4")

    if FINANCIAL_PDF_PATH or SUSTAINABILITY_PDF_PATH:
        print(f"Overall score: {overall:.1f} / 10")

    # 8) Generate summary (only if both financial and sustainability data provided)
    if FINANCIAL_PDF_PATH and SUSTAINABILITY_PDF_PATH:
        llm = get_llm()
        print("\nGenerating investor summary...")
        summary = generate_summary(llm, f_score, s_score, fi, si)
        print("\n=== INVESTOR SUMMARY ===")
        print(summary)
    elif FINANCIAL_PDF_PATH:
        print("\n[Financial-only analysis complete. Add sustainability report for full investor summary.]")
    elif SUSTAINABILITY_PDF_PATH:
        print("\n[Sustainability-only analysis complete. Add financial report for full investor summary.]")


if __name__ == "__main__":
    main()
