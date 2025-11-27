"""
Streamlit web application for automotive company financial and sustainability analysis.
Users can upload PDF reports and get comprehensive analysis with scores and recommendations.
"""

import os
import json
import tempfile
from dataclasses import dataclass
from typing import Dict, Any
from dotenv import load_dotenv

import streamlit as st
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

# --------- CONFIG ---------
MODEL_NAME = "gpt-4o-mini"

if "OPENAI_API_KEY" not in os.environ:
    st.error("OPENAI_API_KEY not found. Please create a .env file with OPENAI_API_KEY=your_key")
    st.stop()

# --------- DATA CLASSES ---------

@dataclass
class FinancialIndicators:
    revenue_growth_score: int | None
    revenue_growth_evidence: str
    gross_margin_score: int | None
    gross_margin_evidence: str
    operating_margin_score: int | None
    operating_margin_evidence: str
    ebitda_margin_score: int | None
    ebitda_margin_evidence: str
    fcf_score: int | None
    fcf_evidence: str
    capex_score: int | None
    capex_evidence: str
    rnd_score: int | None
    rnd_evidence: str
    inventory_score: int | None
    inventory_evidence: str


@dataclass
class SustainabilityIndicators:
    ghg_scope1_reported: bool
    ghg_scope1_evidence: str
    ghg_scope2_reported: bool
    ghg_scope2_evidence: str
    ghg_scope3_reported: bool
    ghg_scope3_evidence: str
    ghg_yoy_change_reported: bool
    ghg_yoy_evidence: str
    ev_production_targets: bool
    ev_targets_evidence: str
    battery_recycling_reported: bool
    battery_recycling_evidence: str
    ice_phaseout_date_specified: bool
    ice_phaseout_evidence: str
    supply_chain_traceability: bool
    supply_chain_evidence: str
    claims_have_specificity: bool
    specificity_evidence: str
    claims_have_supporting_evidence: bool
    supporting_evidence: str
    avoids_excessive_self_praise: bool
    self_praise_evidence: str
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
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)
    return vectorstore


def retrieve_context(question: str, vs: FAISS, k: int = 5) -> str:
    """Retrieve relevant context from the vector store."""
    docs = vs.similarity_search(question, k=k)
    return "\n\n".join([d.page_content for d in docs])


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
    ghg_context = retrieve_context(
        "Scope 1, Scope 2, and Scope 3 greenhouse gas emissions with numeric values and year-on-year changes",
        vs, k=8
    )

    auto_context = retrieve_context(
        "EV production percentages, battery recycling rates, ICE phase-out dates, supply chain traceability",
        vs, k=8
    )

    quality_context = retrieve_context(
        "Sustainability claims, net-zero commitments, water usage, hazardous waste, regulatory fines, supplier audits",
        vs, k=8
    )

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
    """Sum all financial indicator scores. Maximum: 16 points."""
    score = 0
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
    return score


def compute_sustainability_score(si: SustainabilityIndicators) -> int:
    """Sum all sustainability indicator scores. Maximum: 15 points."""
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

    return score


# --------- DISCLOSURE QUALITY MATRIX HELPERS ---------

def compute_disclosure_quality(si: SustainabilityIndicators) -> Dict[str, Any]:
    """
    Compute completeness and reliability levels for the Option 1 matrix.

    Completeness of disclosure:
        - Based on whether key sustainability metrics are reported.
    Reliability of claims:
        - Based on greenwashing-related indicators.
    """
    # Key metrics that represent basic disclosure completeness
    completeness_flags = [
        si.ghg_scope1_reported,
        si.ghg_scope2_reported,
        si.ghg_scope3_reported,
        si.ghg_yoy_change_reported,
        si.ev_production_targets,
        si.battery_recycling_reported,
        si.ice_phaseout_date_specified,
        si.supply_chain_traceability,
        si.water_usage_reported,
        si.hazardous_waste_reported,
        si.regulatory_fines_disclosed,
        si.supplier_audit_frequency,
    ]

    completeness_ratio = sum(completeness_flags) / len(completeness_flags) if completeness_flags else 0.0

    # Claim-quality / anti-greenwashing checks
    reliability_flags = [
        si.claims_have_specificity,
        si.claims_have_supporting_evidence,
        si.avoids_excessive_self_praise,
    ]
    reliability_ratio = sum(reliability_flags) / len(reliability_flags) if reliability_flags else 0.0

    def to_level(r: float) -> str:
        if r >= 0.75:
            return "High"
        elif r >= 0.4:
            return "Medium"
        else:
            return "Low"

    return {
        "completeness_ratio": completeness_ratio,
        "reliability_ratio": reliability_ratio,
        "completeness_level": to_level(completeness_ratio),
        "reliability_level": to_level(reliability_ratio),
    }


def render_disclosure_matrix(quality: Dict[str, Any]):
    """
    Render a 3×3 coloured matrix (Option 1) in Streamlit using HTML.

    X-axis: Completeness of Disclosure (Low → High)
    Y-axis: Reliability of Claims (Low → High)
    Cell text = approximate risk level; current company cell is marked with ⬤.
    """
    completeness_level = quality["completeness_level"]
    reliability_level = quality["reliability_level"]
    completeness_ratio = quality["completeness_ratio"]
    reliability_ratio = quality["reliability_ratio"]

    # Define risk level and colours for each combination
    # (row = reliability, col = completeness)
    levels = ["Low", "Medium", "High"]

    # risk labels roughly following a risk-matrix style
    risk_map = {
        ("Low", "Low"): ("High", "#d73027"),
        ("Low", "Medium"): ("High", "#d73027"),
        ("Low", "High"): ("Med-High", "#f46d43"),
        ("Medium", "Low"): ("High", "#d73027"),
        ("Medium", "Medium"): ("Medium", "#fdae61"),
        ("Medium", "High"): ("Medium", "#fdae61"),
        ("High", "Low"): ("Med-High", "#f46d43"),
        ("High", "Medium"): ("Medium", "#fdae61"),
        ("High", "High"): ("Low", "#66bd63"),
    }

    # Build table rows
    rows_html = ""
    # Show High reliability at top down to Low (like heatmaps with likelihood axis)
    for rel in reversed(levels):
        row_cells = f'<td style="font-weight:600;padding:6px 10px;white-space:nowrap;">{rel} reliability</td>'
        for comp in levels:
            risk_label, bg_color = risk_map[(rel, comp)]
            is_company_cell = (rel == reliability_level and comp == completeness_level)
            border = "2px solid #000" if is_company_cell else "1px solid #dddddd"
            marker = "⬤ " if is_company_cell else ""
            row_cells += (
                f'<td style="border:{border};background-color:{bg_color};'
                f'padding:6px 10px;text-align:center;color:#ffffff;font-weight:600;">'
                f'{marker}{risk_label}</td>'
            )
        rows_html += f"<tr>{row_cells}</tr>"

    table_html = f"""
    <div style="margin-top:0.75rem;">
      <p><strong>Disclosure Quality Matrix</strong></p>
      <p style="font-size:0.9rem;margin-bottom:0.5rem;">
        Completeness of disclosure: <strong>{completeness_level}</strong> ({completeness_ratio*100:.0f}% of key metrics reported)<br>
        Reliability of claims: <strong>{reliability_level}</strong> ({reliability_ratio*100:.0f}% of claim-quality checks passed)
      </p>
      <table style="border-collapse:collapse;">
        <tr>
          <th style="border:none;"></th>
          <th style="padding:6px 10px;">Low completeness</th>
          <th style="padding:6px 10px;">Medium completeness</th>
          <th style="padding:6px 10px;">High completeness</th>
        </tr>
        {rows_html}
      </table>
      <p style="font-size:0.8rem;margin-top:0.4rem;">
        ⬤ marks this company's position. Green cells indicate lower disclosure risk; red cells indicate higher disclosure or greenwashing risk.
      </p>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)


# --------- SUMMARY GENERATION ---------

def generate_summary(
    llm: ChatOpenAI,
    f_score: int,
    s_score: int,
    fi: FinancialIndicators,
    si: SustainabilityIndicators,
) -> str:
    """Generate comprehensive 1-page investor summary."""

    f_score_normalized = (f_score / 16) * 10
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

FORMATTING RULES (IMPORTANT):
- Use markdown headings (##) exactly as requested below.
- Use bullet points with "-" as the bullet.
- You MAY use **bold** ONLY for short labels at the beginning of each bullet, e.g. **Revenue Growth:**.
- DO NOT use italics or any other markdown formatting (no *text*, _text_, or inline code).
- Write normal prose after the bold label in each bullet.
- Ensure there are proper spaces between numbers and units and years, for example:
  "180,683 million in 2024 to 195,201 million in 2025"
  (note the spaces before and after "million" and "in").

Generate a well-structured report with the following sections:

## EXECUTIVE OVERVIEW
2-3 sentences summarizing the company's overall financial health (score: {f_score}/16) and sustainability performance (score: {s_score}/15).

## FINANCIAL ANALYSIS (Score: {f_score}/16, Normalized: {f_norm:.1f}/10)
Provide 4-6 bullet points analyzing:
- Revenue growth trends with specific percentages/figures from evidence
- Profitability metrics (gross, operating, EBITDA margins) with YoY changes
- Cash flow position and capital allocation (FCF, CapEx, R&D as % of revenue)
- Operational efficiency (inventory management)

For each bullet point:
- Start with a short bold label, e.g. **Revenue Growth:**
- Then continue with plain text, including supporting snippets from the evidence fields
  (actual numbers, percentages, or quotes).
- Follow normal spacing conventions between numbers, units, and years.

## SUSTAINABILITY ANALYSIS (Score: {s_score}/15, Normalized: {s_norm:.1f}/10)
Provide 4-6 bullet points analyzing:
- GHG emissions reporting (Scope 1/2/3 coverage and YoY trends)
- EV transition strategy (production targets, ICE phase-out, battery recycling)
- Transparency and greenwashing assessment (specificity of claims, third-party verification)
- Environmental compliance (water, waste, fines, supplier audits)

For each bullet point:
- Start with a short bold label, e.g. **GHG Emissions:**
- Then write plain text with supporting snippets from the evidence fields
  (emissions data, target dates, certifications).

## STRENGTHS
List 3-4 bullet points. Each bullet should start with a short bold label followed by plain text.

## WEAKNESSES
List 3-4 bullet points. Each bullet should start with a short bold label followed by plain text.

## RISK FACTORS
Identify 3-4 material risks based on the financial and sustainability analysis:
- Financial risks (cash burn, margin pressure, inventory issues, etc.)
- Transition risks (EV adoption delays, regulatory changes, etc.)
- ESG risks (emissions trajectory, greenwashing exposure, compliance issues, etc.)
Again, each bullet should have a bold label followed by plain text.

## INVESTMENT RECOMMENDATION
1-2 sentences with overall assessment and readiness for automotive industry transition.
This section should be plain text (no bold or italics inside the sentences).

Keep the entire report under 600 words. Use clear, professional language. Quote specific numbers from evidence fields with proper spacing.
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


# --------- STREAMLIT APP ---------

def main():
    st.set_page_config(
        page_title="Automotive ESG Analyzer",
        page_icon="🚗",
        layout="wide"
    )

    st.title("🚗 Automotive Company Financial & Sustainability Analyzer")
    st.markdown("""
    Upload financial and/or sustainability reports (PDF format) to get comprehensive analysis with:
    - **Financial scoring** (0-16 points across 8 indicators)
    - **Sustainability scoring** (0-15 points across 15 automotive-specific indicators)
    - **Detailed investor summary** with strengths, weaknesses, and risk factors
    """)

    st.divider()

    # File upload section
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Financial Report")
        financial_file = st.file_uploader(
            "Upload Annual Report / 10-K",
            type=["pdf"],
            key="financial",
            help="Upload the company's financial report (annual report, 10-K, etc.)"
        )

    with col2:
        st.subheader("🌱 Sustainability Report")
        sustainability_file = st.file_uploader(
            "Upload ESG / Sustainability Report",
            type=["pdf"],
            key="sustainability",
            help="Upload the company's sustainability or ESG report"
        )

    st.divider()

    # Analyze button
    if st.button("🔍 Analyze Reports", type="primary", use_container_width=True):
        if not financial_file and not sustainability_file:
            st.error("⚠️ Please upload at least one report to analyze.")
            return

        # Initialize variables
        fi = None
        si = None
        f_score = 0
        s_score = 0
        f_score_normalized = 0
        s_score_normalized = 0

        try:
            llm = get_llm()

            # Process financial report
            if financial_file:
                with st.spinner("📊 Analyzing financial report..."):
                    # Save uploaded file to temp directory
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(financial_file.read())
                        financial_path = tmp_file.name

                    # Build vector store and extract indicators
                    financial_vs = build_vectorstore_from_pdf(financial_path)
                    fi = extract_financial_indicators(llm, financial_vs)
                    f_score = compute_financial_score(fi)
                    f_score_normalized = (f_score / 16) * 10

                    # Clean up temp file
                    os.unlink(financial_path)

                st.success("✅ Financial analysis complete!")

            # Process sustainability report
            if sustainability_file:
                with st.spinner("🌱 Analyzing sustainability report..."):
                    # Save uploaded file to temp directory
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(sustainability_file.read())
                        sustainability_path = tmp_file.name

                    # Build vector store and extract indicators
                    sustainability_vs = build_vectorstore_from_pdf(sustainability_path)
                    si = extract_sustainability_indicators(llm, sustainability_vs)
                    s_score = compute_sustainability_score(si)
                    s_score_normalized = (s_score / 15) * 10

                    # Clean up temp file
                    os.unlink(sustainability_path)

                st.success("✅ Sustainability analysis complete!")

            # Calculate overall score
            if financial_file and sustainability_file:
                overall = (f_score_normalized + s_score_normalized) / 2
            elif financial_file:
                overall = f_score_normalized
            elif sustainability_file:
                overall = s_score_normalized
            else:
                overall = 0

            st.divider()

            # Display scores
            st.header("📈 Scores")

            score_col1, score_col2, score_col3 = st.columns(3)

            with score_col1:
                if fi:
                    st.metric(
                        "Financial Score",
                        f"{f_score}/16",
                        f"{f_score_normalized:.1f}/10 normalized"
                    )
                else:
                    st.metric("Financial Score", "N/A", "No report uploaded")

            with score_col2:
                if si:
                    st.metric(
                        "Sustainability Score",
                        f"{s_score}/15",
                        f"{s_score_normalized:.1f}/10 normalized"
                    )
                else:
                    st.metric("Sustainability Score", "N/A", "No report uploaded")

            with score_col3:
                if fi or si:
                    st.metric(
                        "Overall Score",
                        f"{overall:.1f}/10",
                        delta=None
                    )
                else:
                    st.metric("Overall Score", "N/A", "No reports uploaded")

            # Display detailed breakdown
            if fi or si:
                st.divider()

                detail_col1, detail_col2 = st.columns(2)

                with detail_col1:
                    if fi:
                        st.subheader("💰 Financial Breakdown")
                        st.markdown(f"""
                        - **Revenue Growth:** {fi.revenue_growth_score if fi.revenue_growth_score is not None else 'N/A'} / 2  
                        - **Gross Margin:** {fi.gross_margin_score if fi.gross_margin_score is not None else 'N/A'} / 2  
                        - **Operating Margin:** {fi.operating_margin_score if fi.operating_margin_score is not None else 'N/A'} / 2  
                        - **EBITDA Margin:** {fi.ebitda_margin_score if fi.ebitda_margin_score is not None else 'N/A'} / 2  
                        - **Free Cash Flow:** {fi.fcf_score if fi.fcf_score is not None else 'N/A'} / 2  
                        - **CapEx % of Revenue:** {fi.capex_score if fi.capex_score is not None else 'N/A'} / 2  
                        - **R&D % of Revenue:** {fi.rnd_score if fi.rnd_score is not None else 'N/A'} / 2  
                        - **Inventory/DIO:** {fi.inventory_score if fi.inventory_score is not None else 'N/A'} / 2  
                        """)

                with detail_col2:
                    if si:
                        st.subheader("🌍 Sustainability Breakdown")
                        st.markdown(f"""
                        - **GHG Emissions:** {sum([si.ghg_scope1_reported, si.ghg_scope2_reported, si.ghg_scope3_reported, si.ghg_yoy_change_reported])} / 4  
                        - **Automotive Targets:** {sum([si.ev_production_targets, si.battery_recycling_reported, si.ice_phaseout_date_specified, si.supply_chain_traceability])} / 4  
                        - **Transparency:** {sum([si.claims_have_specificity, si.claims_have_supporting_evidence, si.avoids_excessive_self_praise])} / 3  
                        - **Environmental/Compliance:** {sum([si.water_usage_reported, si.hazardous_waste_reported, si.regulatory_fines_disclosed, si.supplier_audit_frequency])} / 4  
                        """)

                # ---- NEW: Disclosure Quality Matrix (Option 1) ----
                if si:
                    st.divider()
                    st.subheader("🧭 Disclosure Quality Risk View")
                    quality = compute_disclosure_quality(si)
                    render_disclosure_matrix(quality)

            # Generate and display summary
            if fi and si:
                st.divider()
                with st.spinner("📝 Generating comprehensive investor summary..."):
                    summary = generate_summary(llm, f_score, s_score, fi, si)

                st.header("📄 Investor Summary")
                st.markdown(summary)

                # Download button for summary
                st.download_button(
                    label="📥 Download Summary as Text",
                    data=summary,
                    file_name="investor_summary.txt",
                    mime="text/plain"
                )

            elif fi:
                st.info("💡 Upload a sustainability report to generate a comprehensive investor summary.")
            elif si:
                st.info("💡 Upload a financial report to generate a comprehensive investor summary.")

            # Expandable raw indicators
            if fi or si:
                st.divider()
                with st.expander("🔍 View Raw Indicators (Debug)"):
                    if fi:
                        st.subheader("Financial Indicators")
                        st.json(fi.__dict__)
                    if si:
                        st.subheader("Sustainability Indicators")
                        st.json(si.__dict__)

        except Exception as e:
            st.error(f"❌ Error during analysis: {str(e)}")
            st.exception(e)


if __name__ == "__main__":
    main()
