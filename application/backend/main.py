
from fastapi import FastAPI, HTTPException
from datetime import datetime, timezone
import time
from pydantic import BaseModel
import sys
from pathlib import Path

# Locate the AIRA incident analyzer directory
ANALYZER_PATH = (
    Path(__file__).resolve().parents[2]
    / "ai-engine"
    / "incident-analyzer"
)

sys.path.insert(0, str(ANALYZER_PATH))

# Import the Python incident analyzer and recovery policy
from analyzer import analyze_incident
from recovery_policy import validate_recovery_action


# Initialize FastAPI application
app = FastAPI(
    title="AIRA - AI-Driven Intelligent Recovery and Deployment Orchestrator",
    description="Sample application for AIRA incident detection and recovery",
    version="1.0.0"
)


# Home endpoint
@app.get("/")
def home():
    return {
        "project": "AIRA",
        "message": "Welcome to AIRA",
        "status": "running"
    }


# Health check endpoint
@app.get("/health")
def health():
    return {
        "application": "aira-api",
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# Version endpoint
@app.get("/version")
def version():
    return {
        "application": "aira-api",
        "version": "1.0.0"
    }


# Sample orders endpoint
@app.get("/api/orders")
def get_orders():
    return {
        "orders": [
            {"order_id": 101, "product": "Laptop"},
            {"order_id": 102, "product": "Keyboard"},
            {"order_id": 103, "product": "Mouse"}
        ]
    }


# Simulate an application error
@app.get("/simulate/error")
def simulate_error():
    raise HTTPException(
        status_code=500,
        detail="Simulated application failure for AIRA testing"
    )


# Simulate a slow application response
@app.get("/simulate/slow")
def simulate_slow():
    time.sleep(3)
    return {
        "application": "aira-api",
        "message": "Slow response simulated",
        "status": "completed"
    }


# Incident request data model
class IncidentRequest(BaseModel):
    incident_id: str
    incident_type: str
    region: str
    service: str
    severity: str
    metrics: dict
    application: dict


# Analyze incident and validate recovery recommendation
@app.post("/analyze-incident")
def analyze_incident_api(incident: IncidentRequest):

    incident_data = incident.model_dump()

    # Analyze incident using the Python rule-based engine
    result = analyze_incident(incident_data)

    # Validate the recommended recovery action
    policy_result = validate_recovery_action(result)

    return {
        "project": "AIRA",
        "message": "Incident analysis completed",
        "analysis": result,
        "recovery_policy": policy_result
    }
