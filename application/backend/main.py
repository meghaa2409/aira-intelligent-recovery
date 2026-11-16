
import os
import json
import time
import sys
import uuid
import secrets
import boto3

from pathlib import Path
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field

# --------------------------------------------------
# LOCATE AI INCIDENT ANALYZER
# --------------------------------------------------

ANALYZER_PATH = (
    Path(__file__).resolve().parents[2]
    / "ai-engine"
    / "incident-analyzer"
)

sys.path.insert(0, str(ANALYZER_PATH))

from analyzer import analyze_incident
from recovery_policy import validate_recovery_action


# --------------------------------------------------
# APPLICATION CONFIGURATION
# --------------------------------------------------

app = FastAPI(
    title="AIRA - AI-Driven Intelligent Recovery and Deployment Orchestrator",
    description="AI-assisted incident analysis and controlled AWS recovery",
    version="1.1.0"
)


# --------------------------------------------------
# AWS CONFIGURATION
# --------------------------------------------------

AWS_REGION = os.environ.get(
    "AWS_REGION",
    "ap-south-1"
)

STATE_MACHINE_ARN = os.environ.get(
    "STATE_MACHINE_ARN",
    "arn:aws:states:ap-south-1:016279724502:stateMachine:aira-recovery-workflow"
)

APPROVAL_SECRET = os.environ.get("APPROVAL_SECRET")

sfn = boto3.client(
    "stepfunctions",
    region_name=AWS_REGION
)


# --------------------------------------------------
# HOME ENDPOINT
# --------------------------------------------------

@app.get("/")
def home():

    return {
        "project": "AIRA",
        "message": "Welcome to AIRA",
        "status": "running"
    }


# --------------------------------------------------
# APPLICATION HEALTH
# --------------------------------------------------

@app.get("/health")
def health():

    return {
        "application": "aira-api",
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# --------------------------------------------------
# VERSION ENDPOINT
# --------------------------------------------------

@app.get("/version")
def version():

    return {
        "application": "aira-api",
        "version": "1.1.0"
    }


# --------------------------------------------------
# SAMPLE ORDERS
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
# SIMULATE APPLICATION ERROR
# --------------------------------------------------

@app.get("/simulate/error")
def simulate_error():

    raise HTTPException(
        status_code=500,
        detail="Simulated application failure for AIRA testing"
    )


# --------------------------------------------------
# SIMULATE SLOW RESPONSE
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
# INCIDENT REQUEST MODEL
# --------------------------------------------------

class IncidentRequest(BaseModel):

    incident_id: str
    incident_type: str
    region: str
    service: str
    severity: str
    metrics: dict
    application: dict


# --------------------------------------------------
# INCIDENT ANALYSIS API
# --------------------------------------------------

@app.post("/analyze-incident")
def analyze_incident_api(incident: IncidentRequest):

    incident_data = incident.model_dump()

    # AI incident analysis
    result = analyze_incident(incident_data)

    # Validate recovery recommendation
    policy_result = validate_recovery_action(result)

    return {
        "project": "AIRA",
        "message": "Incident analysis completed",
        "analysis": result,
        "recovery_policy": policy_result
    }


# --------------------------------------------------
# HUMAN APPROVAL REQUEST MODEL
# --------------------------------------------------

class RecoveryApprovalRequest(BaseModel):

    incident_id: str
    action: str = "scale_ecs"
    desired_count: int = Field(default=2, ge=1, le=3)
    approved_by: str = Field(min_length=1, max_length=100)


# --------------------------------------------------
# HUMAN REJECTION REQUEST MODEL
# --------------------------------------------------

class RecoveryRejectionRequest(BaseModel):

    incident_id: str
    action: str = "scale_ecs"
    rejected_by: str = Field(min_length=1, max_length=100)


# --------------------------------------------------
# VERIFY APPROVAL AUTHENTICATION
# --------------------------------------------------

def verify_approval_secret(secret):

    if not APPROVAL_SECRET:

        raise HTTPException(
            status_code=503,
            detail="Approval authentication is not configured."
        )

    if not secrets.compare_digest(
        secret or "",
        APPROVAL_SECRET
    ):

        raise HTTPException(
            status_code=401,
            detail="Unauthorized approval request."
        )


# --------------------------------------------------
# START STEP FUNCTIONS WORKFLOW
# --------------------------------------------------

def start_recovery_workflow(payload):

    try:

        response = sfn.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            name="aira-" + uuid.uuid4().hex,
            input=json.dumps(payload)
        )

        return {
            "status": "workflow_started",
            "incident_id": payload["incident_id"],
            "execution_arn": response["executionArn"],
            "start_date": response["startDate"].isoformat(),
            "recovery_executed": False
        }

    except Exception:

        # Do not expose AWS exception details to API clients.
        raise HTTPException(
            status_code=502,
            detail="Could not start AIRA recovery workflow."
        )


# --------------------------------------------------
# APPROVE RECOVERY
# --------------------------------------------------

@app.post("/recovery/approve")
def approve_recovery(
    request: RecoveryApprovalRequest,
    x_approval_secret: str = Header(default=None)
):

    verify_approval_secret(x_approval_secret)

    if not request.incident_id.strip():

        raise HTTPException(
            status_code=400,
            detail="Incident ID is required."
        )

    if not request.approved_by.strip():

        raise HTTPException(
            status_code=400,
            detail="Approver identity is required."
        )

    if request.action != "scale_ecs":

        raise HTTPException(
            status_code=400,
            detail="Unsupported recovery action."
        )

    payload = {
        "incident_id": request.incident_id,
        "action": request.action,
        "desired_count": request.desired_count,
        "approved": True,
        "approved_by": request.approved_by,

        # Safety: approval integration testing only.
        "dry_run": True
    }

    return start_recovery_workflow(payload)


# --------------------------------------------------
# REJECT RECOVERY
# --------------------------------------------------

@app.post("/recovery/reject")
def reject_recovery(
    request: RecoveryRejectionRequest,
    x_approval_secret: str = Header(default=None)
):

    verify_approval_secret(x_approval_secret)

    if not request.incident_id.strip():

        raise HTTPException(
            status_code=400,
            detail="Incident ID is required."
        )

    if not request.rejected_by.strip():

        raise HTTPException(
            status_code=400,
            detail="Rejector identity is required."
        )

    if request.action != "scale_ecs":

        raise HTTPException(
            status_code=400,
            detail="Unsupported recovery action."
        )

    payload = {
        "incident_id": request.incident_id,
        "action": request.action,
        "desired_count": 2,
        "approved": False,
        "dry_run": False
    }

    return start_recovery_workflow(payload)


# --------------------------------------------------
# RECOVERY INTEGRATION HEALTH
# --------------------------------------------------

@app.get("/recovery/health")
def recovery_health():

    return {
        "component": "AIRA Recovery Approval API",
        "status": "healthy",
        "workflow_configured": bool(STATE_MACHINE_ARN),
        "approval_authentication_configured": bool(
            APPROVAL_SECRET
        ),
        "execution_mode": "dry_run"
    }