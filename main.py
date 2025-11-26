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

# Set to None to skip financial analysis
FINANCIAL_PDF_PATH = None  # "C:/Users/nancy/OneDrive - Yale University/Documents/1. School/4. Yale MAM/3. Academics/MGT 695/CPSC-1710-Final-Project/data/TSLA_2024_Annual_Report.pdf"
SUSTAINABILITY_PDF_PATH = "C:/Users/nancy/OneDrive - Yale University/Documents/1. School/4. Yale MAM/3. Academics/MGT 695/CPSC-1710-Final-Project/data/RIVN_2024_Environmental_Metrics_Report.pdf"

MODEL_NAME = "gpt-4o-mini"  # option to switch to gpt-4o (more expensive)

if "OPENAI_API_KEY" not in os.environ:
    raise RuntimeError(
        "OPENAI_API_KEY not found. Make sure you created a .env file with OPENAI_API_KEY=your_key"
    )

# --------- DATA CLASSES ---------

# All the financial boolean indicators plus a short evidence string for each.
@dataclass
class FinancialIndicators:
    revenue_growth_positive: bool
    revenue_growth_evidence: str
    margin_stable_or_improving: bool
    margin_evidence: str
    fcf_positive_or_operating_cf_positive: bool
    fcf_evidence: str
    leverage_not_rising: bool
    leverage_evidence: str
    specific_forward_guidance: bool
    guidance_evidence: str


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
        "Information about revenue growth, margins, cash flow, leverage/net debt "
        "and forward-looking guidance with numbers or dates."
    )

    context = retrieve_context(question, vs, k=8)

    prompt = ChatPromptTemplate.from_template(
        """
You are an analyst reading a company's financial report.

CONTEXT:
{context}

Return a STRICT JSON object with exactly these keys and types:

- revenue_growth_positive: true or false
- revenue_growth_evidence: string
- margin_stable_or_improving: true or false
- margin_evidence: string
- fcf_positive_or_operating_cf_positive: true or false
- fcf_evidence: string
- leverage_not_rising: true or false
- leverage_evidence: string
- specific_forward_guidance: true or false
- guidance_evidence: string

The output MUST be valid JSON, with double-quoted keys and values where appropriate, for example:

{{
  "revenue_growth_positive": true,
  "revenue_growth_evidence": "...",
  ...
}}

Definitions:
- revenue_growth_positive: revenue increased year-on-year.
- margin_stable_or_improving: operating/profit margins are stable or increasing.
- fcf_positive_or_operating_cf_positive: free cash flow is positive OR, if not given,
  operating cash flow is positive.
- leverage_not_rising: net debt or leverage is stable or decreasing.
- specific_forward_guidance: numeric or dated guidance is provided (e.g. percentages,
  revenue ranges, EPS targets, or specific years).

If unclear, answer false and explain the ambiguity in the evidence string.

ONLY output the JSON object, no extra text.
        """
    )

    chain = prompt | llm
    resp = chain.invoke({"context": context})
    data: Dict[str, Any] = json.loads(resp.content)

    return FinancialIndicators(
        revenue_growth_positive=data["revenue_growth_positive"],
        revenue_growth_evidence=data["revenue_growth_evidence"],
        margin_stable_or_improving=data["margin_stable_or_improving"],
        margin_evidence=data["margin_evidence"],
        fcf_positive_or_operating_cf_positive=data["fcf_positive_or_operating_cf_positive"],
        fcf_evidence=data["fcf_evidence"],
        leverage_not_rising=data["leverage_not_rising"],
        leverage_evidence=data["leverage_evidence"],
        specific_forward_guidance=data["specific_forward_guidance"],
        guidance_evidence=data["guidance_evidence"],
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
    score = 0
    if fi.revenue_growth_positive:
        score += 1
    if fi.margin_stable_or_improving:
        score += 1
    if fi.fcf_positive_or_operating_cf_positive:
        score += 1
    if fi.leverage_not_rising:
        score += 1
    if fi.specific_forward_guidance:
        score += 1
    return score


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

    # Normalize scores for comparison (both on 0-10 scale)
    f_score_normalized = (f_score / 5) * 10
    s_score_normalized = (s_score / 15) * 10
    overall = (f_score_normalized + s_score_normalized) / 2

    payload = {
        "financial_score": f_score,
        "financial_score_out_of": 5,
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
You are writing a concise investor note for an AUTOMOTIVE company.

Here are structured scores and evidence:
{payload_json}

Write:
1) A 2–4 sentence overview of the automaker's financial and sustainability health.
2) 3–5 bullet points highlighting:
   - Financial strengths/risks
   - GHG emissions transparency
   - EV transition progress
   - Greenwashing red flags (if any)
   - Environmental compliance
3) A conclusion sentence about the company's readiness for the automotive transition.

Keep everything under 300 words.
        """
    )

    chain = prompt | llm
    resp = chain.invoke({"payload_json": json.dumps(payload, indent=2)})
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
        f_score_normalized = (f_score / 5) * 10
    else:
        print("\n[Skipping financial analysis - no financial report provided]")

    # 2) Build vector store for sustainability report
    sustainability_vs = build_vectorstore_from_pdf(SUSTAINABILITY_PDF_PATH)

    # 3) Create LLM client
    llm = get_llm()

    # 4) Extract sustainability indicators
    print("\nExtracting sustainability indicators...")
    si = extract_sustainability_indicators(llm, sustainability_vs)

    # 5) Compute scores
    s_score = compute_sustainability_score(si)
    s_score_normalized = (s_score / 15) * 10

    # Calculate overall score
    if FINANCIAL_PDF_PATH:
        overall = (f_score_normalized + s_score_normalized) / 2
    else:
        overall = s_score_normalized

    # 6) Print raw indicators (debug)
    print("\n--- RAW INDICATORS ---")
    if fi:
        print("FINANCIAL:")
        print(fi)
        print("\n")
    print("SUSTAINABILITY:")
    print(si)

    # 7) Print scores
    print("\n--- SCORES ---")
    if FINANCIAL_PDF_PATH:
        print(f"Financial score: {f_score} / 5 (normalized: {f_score_normalized:.1f} / 10)")
    print(f"Sustainability score: {s_score} / 15 (normalized: {s_score_normalized:.1f} / 10)")
    print(f"  - GHG Emissions: {sum([si.ghg_scope1_reported, si.ghg_scope2_reported, si.ghg_scope3_reported, si.ghg_yoy_change_reported])} / 4")
    print(f"  - Automotive Targets: {sum([si.ev_production_targets, si.battery_recycling_reported, si.ice_phaseout_date_specified, si.supply_chain_traceability])} / 4")
    print(f"  - Transparency: {sum([si.claims_have_specificity, si.claims_have_supporting_evidence, si.avoids_excessive_self_praise])} / 3")
    print(f"  - Environmental/Compliance: {sum([si.water_usage_reported, si.hazardous_waste_reported, si.regulatory_fines_disclosed, si.supplier_audit_frequency])} / 4")
    print(f"Overall score: {overall:.1f} / 10")

    # 8) Generate summary (only if financial data provided)
    if FINANCIAL_PDF_PATH:
        print("\nGenerating investor summary...")
        summary = generate_summary(llm, f_score, s_score, fi, si)
        print("\n=== INVESTOR SUMMARY ===")
        print(summary)
    else:
        print("\n[Sustainability-only analysis complete. Add financial report for full investor summary.]")


if __name__ == "__main__":
    main()
