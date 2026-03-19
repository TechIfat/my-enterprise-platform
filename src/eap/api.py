from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from eap.agent import get_agent_response

# 1. Initialize the Enterprise API
app = FastAPI(
    title="Enterprise Agentic Platform API",
    description="REST API wrapping the LangGraph Multi-Agent Swarm",
    version="1.0.0"
)
# --- NEW: HEALTH CHECK ENDPOINT ---
@app.get("/")
async def root():
    """Health check endpoint to verify the API is running."""
    return {"status": "online", "message": "Welcome to the Enterprise Agentic Platform (EAP) API", "docs_url": "/docs"}

# 2. Define strict input/output schemas
class ChatRequest(BaseModel):
    query: str
    session_id: str = "api_session_001"

class ChatResponse(BaseModel):
    response: str
    session_id: str

# 3. Create the Endpoint
@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        print(f"📥 API RECEIVED: {request.query}[Session: {request.session_id}]")
        
        # Trigger the LangGraph Swarm
        answer = await get_agent_response(request.query, request.session_id)
        
        print("📤 API RESPONDING WITH SWARM OUTPUT.")
        return ChatResponse(response=answer, session_id=request.session_id)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Start the web server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)