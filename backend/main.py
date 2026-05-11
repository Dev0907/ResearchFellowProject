from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
from crew.founder_crew import FounderCrew

load_dotenv()

app = FastAPI(title="Founder Simulator API")

# CORS configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StartupIdea(BaseModel):
    idea: str
    problem: Optional[str] = None
    audience: Optional[str] = None
    website: Optional[str] = None
    startup_name: Optional[str] = None

class AnalysisResponse(BaseModel):
    status: str
    report: dict

@app.get("/")
async def root():
    return {
        "message": "Founder Simulator API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_startup(startup: StartupIdea):
    """
    Analyze a startup idea using multi-agent system
    """
    try:
        # Initialize the founder crew
        crew = FounderCrew(
            idea=startup.idea,
            problem=startup.problem,
            audience=startup.audience,
            website=startup.website,
            startup_name=startup.startup_name
        )
        
        # Run the analysis
        result = crew.run()
        
        # result is now {"status": "success", "report": report_data}
        return AnalysisResponse(
            status=result.get("status", "error"),
            report=result.get("report", result)
        )
    
    except Exception as e:
        return AnalysisResponse(
            status="error",
            report={"error": str(e)}
        )

@app.get("/api/examples")
async def get_examples():
    """
    Get example startup ideas for inspiration
    """
    return {
        "examples": [
            {
                "name": "RetailAI",
                "idea": "AI assistant for Indian retail investors",
                "problem": "Retail investors lack personalized guidance",
                "audience": "First-time investors in India"
            },
            {
                "name": "DevFlow",
                "idea": "AI-powered code review automation",
                "problem": "Manual code reviews are slow and inconsistent",
                "audience": "Engineering teams at startups"
            },
            {
                "name": "HealthTrack",
                "idea": "Personalized nutrition tracking using AI",
                "problem": "Generic diet plans don't work for everyone",
                "audience": "Health-conscious millennials"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
