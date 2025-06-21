from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.adk.runners import InMemoryRunner
from google.adk.agents.invocation_context import InvocationContext
from google.adk.sessions import InMemorySessionService  # <-- Add this import
from StockAdvisorApp.agents.agent import root_agent  # Update this import
import os
import uuid

app = FastAPI(title="Stock Advisory System")

class UserProfile(BaseModel):
    age: int
    dependents: int
    monthly_savings: float
    investment_amount: float
    risk_level: str = "medium"

class StockResponse(BaseModel):
    suggested_stocks: list
    shortlisted_stocks: list
    investment_advice: dict

@app.post("/analyze-stocks", response_model=StockResponse)
async def analyze_stocks(profile: UserProfile):
    runner = InMemoryRunner(root_agent)
    session_service = InMemorySessionService()  # <-- Use this
    context = InvocationContext(
        agent=root_agent,
        invocation_id=str(uuid.uuid4()),
        session_service=session_service
    )
    # Set user profile in context
    context.state.update({
        "age": profile.age,
        "dependents": profile.dependents,
        "monthly_savings": profile.monthly_savings,
        "investment_amount": profile.investment_amount,
        "risk_level": profile.risk_level
    })
    
    results = {
        "suggested_stocks": [],
        "shortlisted_stocks": [],
        "investment_advice": {}
    }
    
    try:
        async for event in runner.run(context):
            if event.agent_name == "StockAdvisorAgent":
                results["stocks_types"] = event.data
            elif event.agent_name == "StockAgent":
                results["suggested_stocks"] = event.data
            elif event.agent_name == "StockReviewerAgent1":
                results["shortlisted_stocks"] = event.data
            elif event.agent_name == "StockReviewerAgent2":
                results["investment_advice"] = event.data
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)