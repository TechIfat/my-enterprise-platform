import sqlite3
import os
from dotenv import load_dotenv
# Load environment variables for OpenAI Embeddings
load_dotenv()
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from fastmcp import FastMCP
from pydantic import Field
import random
import re

# Initialize the Server
# "Financial Service" is the name of this microservice in your platform
mcp = FastMCP("Financial Service")

@mcp.tool()
def get_stock_price(ticker: str = Field(..., description="The stock ticker symbol (e.g., AAPL, NVDA)")) -> str:
    """
    Retrieves the current stock price for a given ticker.
    In production, this would hit a real API (Bloomberg/Yahoo).
    """
    # 1. Input Sanitization (Security Pattern)
    # Allow only uppercase letters, 1-5 chars
    if not re.match(r'^[A-Z]{1,5}$', ticker):
        return "Error: Invalid ticker format. Use 1-5 uppercase letters."
        
    # 2. Business Logic
    
    # SIMULATION for Day 1 to ensure connectivity
    # We will replace this with real API calls later
    print(f"--- Log: Querying price for {ticker} ---")
    
    # Mock data generation
    base_price = random.uniform(100, 1000)
    return f"The current price of {ticker.upper()} is ${base_price:.2f}"

@mcp.tool()
def get_company_risk_profile(ticker: str) -> str:

    """
    Retrieves the risk profile (Low/Medium/High) based on volatility.
    """
    risk = random.choice(["Low", "Medium", "High", "Critical"])
    return f"Risk Profile for {ticker.upper()}: {risk}"

@mcp.tool()
def search_internal_knowledge_base(query: str) -> str:
    """
    Searches the bank's internal proprietary knowledge base for compliance rules, 
    risk guidelines, and trading policies.
    """
    print(f"--- Log: Searching internal DB for: {query} ---")
    
    # 1. Connect to the existing Vector Database
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma(
        persist_directory="./chroma_db", 
        embedding_function=embeddings
    )
    
    # 2. Perform a similarity search (Find the top 1 most relevant document)
    docs = vectorstore.similarity_search(query, k=1)
    
    if docs:
        best_match = docs[0]
        return f"INTERNAL POLICY FOUND: {best_match.page_content} (Source: {best_match.metadata['source']})"
    
    return "No relevant internal policies found for this query."

@mcp.tool()
def check_account_balance(client_id: str) -> str:
    """
    Queries the legacy SQL mainframe to check a client's available cash balance and tier.
    Requires the exact client_id (e.g., C-12345).
    """
    print(f"--- Log: Querying Mainframe SQL for Client {client_id} ---")
    try:
        conn = sqlite3.connect("mainframe.db")
        cursor = conn.cursor()
        
        # DEVSECOPS PATTERN: We use parameterised queries (?,) to absolutely prevent SQL Injection attacks.
        cursor.execute("SELECT name, balance, tier FROM accounts WHERE client_id=?", (client_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return f"CLIENT FOUND: {result[0]} | TIER: {result[2]} | AVAILABLE CASH: ${result[1]:.2f}"
        return f"ERROR: Client ID {client_id} not found in mainframe."
    
    except Exception as e:
        return f"MAINFRAME ERROR: {str(e)}"

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
