import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

load_dotenv()

print("🌱 Seeding Enterprise Knowledge Base...")

# 1. Mock Enterprise Proprietary Data (In reality, this would be thousands of PDFs)
proprietary_docs =[
    Document(
        page_content="COMPLIANCE POLICY: Any client stock purchase exceeding $10,000 in a single transaction requires manual sign-off from the Senior Compliance Officer.", 
        metadata={"source": "compliance_policy_v2_2026.pdf"}
    ),
    Document(
        page_content="RISK GUIDELINE: When evaluating tech stocks (like AAPL or NVDA), the Risk Assessor must explicitly state that semiconductor supply chains are currently volatile.", 
        metadata={"source": "Q1_risk_memo.docx"}
    ),
    Document(
        page_content="TRADING RULE: Cryptocurrencies are strictly prohibited for Tier 1 Banking clients.", 
        metadata={"source": "trading_rules.md"}
    )
]

# 2. Convert text to Mathematical Vectors (Embeddings) and store in ChromaDB
vectorstore = Chroma.from_documents(
    documents=proprietary_docs,
    embedding=OpenAIEmbeddings(), # Uses your existing OPENAI_API_KEY
    persist_directory="./chroma_db" # Saves the database to your hard drive
)

print("✅ Knowledge Base Seeded Successfully in './chroma_db'!")