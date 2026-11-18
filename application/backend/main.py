
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import sys
import time
import uuid

import boto3
from botocore.exceptions import ClientError
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# --------------------------------------------------
# 1. Locate the AIRA Incident Analyzer
# --------------------------------------------------

ANALYZER_PATH = (
    Path(__file__).resolve().parents[2]
    / "ai-engine"
    / "incident-analyzer"
)

sys.path.insert(0, str(ANALYZER_PATH))


# --------------------------------------------------
# 2. Import Analyzer and Recovery Policy
# --------------------------------------------------

from analyzer import analyze_incident
from recovery_policy import validate_recovery_action


# --------------------------------------------------
# 3. Initialize FastAPI Application
# --------------------------------------------------

app = FastAPI(
    title="AIRA - AI-Driven Intelligent Recovery and Deployment Orchestrator",
    description="Sample application for AIRA incident detection and recovery",
    version="1.0.0"
)


# --------------------------------------------------
# 4. AWS Step Functions Configuration
# --------------------------------------------------

AWS_REGION = "ap-south-1"

STATE_MACHINE_ARN = os.getenv(
    "AIRA_STATE_MACHINE_ARN",
    "arn:aws:states:ap-south-1:016279724502:stateMachine:aira-recovery-workflow"
)

sfn_client = boto3.client(
    "stepfunctions",
    region_name=AWS_REGION
)


# --------------------------------------------------
# 5. Request Models
# --------------------------------------------------

class IncidentRequest(BaseModel):
    incident_id: str
    incident_type: str
    region: str
    service: str
    severity: str
    metrics: dict
    application: dict


class RecoveryDecisionRequest(BaseModel):
    incident_id: str
    reason: str
    recovery_action: str


# --------------------------------------------------
# 6. Home Endpoint
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "project": "AIRA",
        "message": "Welcome to AIRA",
        "status": "running"
    }


# --------------------------------------------------
# 7. Health Check Endpoint
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "application": "aira-api",
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# --------------------------------------------------
# 8. Version Endpoint
# --------------------------------------------------

@app.get("/version")
def version():
    return {
        "application": "aira-api",
        "version": "1.0.0"
    }


# --------------------------------------------------
# 9. Sample Orders Endpoint
# --------------------------------------------------

@app.get("/api/orders")
def get_orders():
    return {
        "orders": [
            {"order_id": 101, "product": "Laptop"},
            {"order_id": 102, "product": "Keyboard"},
            {"order_id": 103, "product": "Mouse"}
        ]
    }


# --------------------------------------------------
# 10. Simulate Application Error
# --------------------------------------------------

@app.get("/simulate/error")
def simulate_error():
    raise HTTPException(
        status_code=500,
        detail="Simulated application failure for AIRA testing"
    )


# --------------------------------------------------
# 11. Simulate Slow Application Response
# --------------------------------------------------

@app.get("/simulate/slow")
def simulate_slow():
    time.sleep(3)

    return {
        "application": "aira-api",
        "message": "Slow response simulated",
        "status": "completed"
    }


# --------------------------------------------------
# 12. Analyze Incident
# --------------------------------------------------

@app.post("/analyze-incident")
def analyze_incident_api(incident: IncidentRequest):

    incident_data = incident.model_dump()

    # Analyze the incident using the Python rule-based engine
    result = analyze_incident(incident_data)

    # Validate the recommended recovery action
    policy_result = validate_recovery_action(result)

    return {
        "project": "AIRA",
        "message": "Incident analysis completed",
        "analysis": result,
        "recovery_policy": policy_result
    }


# --------------------------------------------------
# 13. Start Recovery Workflow
# --------------------------------------------------

def start_recovery_workflow(
    decision: str,
    request: RecoveryDecisionRequest
):

    execution_input = {
        "decision": decision,
        "incident_id": request.incident_id,
        "reason": request.reason,
        "recovery_action": request.recovery_action
    }

    try:
        response = sfn_client.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            name=f"aira-{decision}-{uuid.uuid4().hex[:12]}",
            input=json.dumps(execution_input)
        )

        return {
            "execution_arn": response["executionArn"],
            "start_date": response["startDate"].isoformat(),
            "status": "STARTED"
        }

    except ClientError as error:
        error_message = error.response.get(
            "Error", {}
        ).get(
            "Message", "Unable to start recovery workflow"
        )

        raise HTTPException(
            status_code=500,
            detail=error_message
        )


# --------------------------------------------------
# 14. Recovery Approval Endpoint
# --------------------------------------------------

@app.post("/recovery/approve")
def approve_recovery(request: RecoveryDecisionRequest):

    result = start_recovery_workflow(
        "approve",
        request
    )

    return {
        "message": "Recovery approval workflow initiated",
        **result
    }


# --------------------------------------------------
# 15. Recovery Rejection Endpoint
# --------------------------------------------------

@app.post("/recovery/reject")
def reject_recovery(request: RecoveryDecisionRequest):

    result = start_recovery_workflow(
        "reject",
        request
    )

    return {
        "message": "Recovery rejection workflow initiated",
        **result
    }
