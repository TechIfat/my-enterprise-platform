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

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
