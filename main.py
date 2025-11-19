import os
import json
from dataclasses import dataclass
from typing import Dict, Any

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate

# --------- CONFIG: PDF paths and model name ---------

FINANCIAL_PDF_PATH = "C:\Users\nancy\OneDrive - Yale University\Documents\1. School\4. Yale MAM\3. Academics\MGT 695\CPSC-1710-Final-Project\data\TSLA_2024_Annual_Report.pdf"
SUSTAINABILITY_PDF_PATH = "C:\Users\nancy\OneDrive - Yale University\Documents\1. School\4. Yale MAM\3. Academics\MGT 695\CPSC-1710-Final-Project\data\TSLA_2024_Impact_Report.pdf"

MODEL_NAME = "gpt-4o-mini"  # you can switch to gpt-4o if you want


if "OPENAI_API_KEY" not in os.environ:
    raise RuntimeError(
        "OPENAI_API_KEY not found. Set it in your terminal before running main.py."
    )


# --------- DATA CLASSES ---------

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


@dataclass
class SustainabilityIndicators:
    scope1_2_reported_with_numbers: bool
    scope1_2_evidence: str
    scope3_reported_or_justified: bool
    scope3_evidence: str
    has_dated_quantitative_target: bool
    target_evidence: str
    shows_progress_toward_target: bool
    progress_evidence: str
    external_assurance_mentioned: bool
    assurance_evidence: str


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
    embeddings = OpenAIEmbeddings()
    vs = FAISS.from_documents(docs, embeddings)
    print("Vector store built.")
    return vs


def retrieve_context(question: str, vectorstore: FAISS, k: int = 8) -> str:
    """Retrieve top-k chunks for a question and join them into one context string."""
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    docs = retriever.get_relevant_documents(question)
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

Return a STRICT JSON object with this schema:

{{
  "revenue_growth_positive": true/false,
  "revenue_growth_evidence": "string",
  "margin_stable_or_improving": true/false,
  "margin_evidence": "string",
  "fcf_positive_or_operating_cf_positive": true/false,
  "fcf_evidence": "string",
  "leverage_not_rising": true/false,
  "leverage_evidence": "string",
  "specific_forward_guidance": true/false,
  "guidance_evidence": "string"
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
    question = (
        "Information about Scope 1 and 2 and 3 greenhouse gas emissions, "
        "emissions or climate targets, progress against those targets, "
        "and external assurance of ESG or emissions data."
    )
    context = retrieve_context(question, vs, k=8)

    prompt = ChatPromptTemplate.from_template(
        """
You are an ESG analyst reading a company's sustainability report.

CONTEXT:
{context}

Return a STRICT JSON object with this schema:

{{
  "scope1_2_reported_with_numbers": true/false,
  "scope1_2_evidence": "string",
  "scope3_reported_or_justified": true/false,
  "scope3_evidence": "string",
  "has_dated_quantitative_target": true/false,
  "target_evidence": "string",
  "shows_progress_toward_target": true/false,
  "progress_evidence": "string",
  "external_assurance_mentioned": true/false,
  "assurance_evidence": "string"
}}

Definitions:
- scope1_2_reported_with_numbers: Scope 1 and/or 2 emissions are reported with numeric values.
- scope3_reported_or_justified: Scope 3 emissions are reported with numbers OR the company
  clearly explains why Scope 3 is not yet included.
- has_dated_quantitative_target: at least one climate/emissions/energy target that is both
  dated and quantitative (e.g. "-30% by 2030").
- shows_progress_toward_target: current year shows any progress toward the target
  (reduced emissions %, improved intensity, etc.).
- external_assurance_mentioned: external/third-party assurance of sustainability or
  emissions data is mentioned.

If unclear, answer false and explain the ambiguity in the evidence string.

ONLY output the JSON object, no extra text.
        """
    )

    chain = prompt | llm
    resp = chain.invoke({"context": context})
    data: Dict[str, Any] = json.loads(resp.content)

    return SustainabilityIndicators(
        scope1_2_reported_with_numbers=data["scope1_2_reported_with_numbers"],
        scope1_2_evidence=data["scope1_2_evidence"],
        scope3_reported_or_justified=data["scope3_reported_or_justified"],
        scope3_evidence=data["scope3_evidence"],
        has_dated_quantitative_target=data["has_dated_quantitative_target"],
        target_evidence=data["target_evidence"],
        shows_progress_toward_target=data["shows_progress_toward_target"],
        progress_evidence=data["progress_evidence"],
        external_assurance_mentioned=data["external_assurance_mentioned"],
        assurance_evidence=data["assurance_evidence"],
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
    score = 0
    if si.scope1_2_reported_with_numbers:
        score += 1
    if si.scope3_reported_or_justified:
        score += 1
    if si.has_dated_quantitative_target:
        score += 1
    if si.shows_progress_toward_target:
        score += 1
    if si.external_assurance_mentioned:
        score += 1
    return score


# --------- SUMMARY GENERATION ---------

def generate_summary(
    llm: ChatOpenAI,
    f_score: int,
    s_score: int,
    fi: FinancialIndicators,
    si: SustainabilityIndicators,
) -> str:
    overall = (f_score + s_score) / 2
    payload = {
        "financial_score": f_score,
        "sustainability_score": s_score,
        "overall_score": overall,
        "financial_indicators": fi.__dict__,
        "sustainability_indicators": si.__dict__,
    }

    prompt = ChatPromptTemplate.from_template(
        """
You are writing a concise investor note.

Here are structured scores and evidence:
{payload_json}

Write:
1) A 2–4 sentence overview of the company's financial and sustainability health.
2) 3–5 bullet points with key strengths and risks (mix of financial and ESG).
3) A one-sentence conclusion saying whether the company appears stronger on
   financial performance, on sustainability, or balanced on both.

Be specific and neutral. Keep everything under 250 words.
        """
    )

    chain = prompt | llm
    resp = chain.invoke({"payload_json": json.dumps(payload, indent=2)})
    return resp.content.strip()


# --------- MAIN ---------

def main():
    financial_vs = build_vectorstore_from_pdf(FINANCIAL_PDF_PATH)
    sustainability_vs = build_vectorstore_from_pdf(SUSTAINABILITY_PDF_PATH)

    llm = get_llm()

    print("\nExtracting financial indicators...")
    fi = extract_financial_indicators(llm, financial_vs)

    print("\nExtracting sustainability indicators...")
    si = extract_sustainability_indicators(llm, sustainability_vs)

    f_score = compute_financial_score(fi)
    s_score = compute_sustainability_score(si)
    overall = (f_score + s_score) / 2

    print("\n--- RAW INDICATORS ---")
    print(fi)
    print(si)

    print("\n--- SCORES ---")
    print(f"Financial score (F): {f_score} / 5")
    print(f"Sustainability score (S): {s_score} / 5")
    print(f"Overall score: {overall:.1f} / 5")

    print("\nGenerating investor summary...")
    summary = generate_summary(llm, f_score, s_score, fi, si)
    print("\n=== INVESTOR SUMMARY ===")
    print(summary)


if __name__ == "__main__":
    main()
