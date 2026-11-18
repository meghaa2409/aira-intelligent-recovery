
import os
import json
import time
import sys
import uuid
import secrets
import boto3
from botocore.exceptions import ClientError

from pathlib import Path
from datetime import datetime, timezone, timedelta

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

ECS_CLUSTER = os.environ.get("ECS_CLUSTER", "aira-cluster")
ECS_SERVICE = os.environ.get("ECS_SERVICE", "aira-service")

sfn = boto3.client(
    "stepfunctions",
    region_name=AWS_REGION
)

cloudwatch_client = boto3.client(
    "cloudwatch",
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


# 13. Retrieve ECS Metrics from CloudWatch
# --------------------------------------------------

def get_ecs_metric(metric_name: str):

    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(minutes=30)

    response = cloudwatch_client.get_metric_statistics(
        Namespace="AWS/ECS",
        MetricName=metric_name,
        Dimensions=[
            {
                "Name": "ClusterName",
                "Value": ECS_CLUSTER
            },
            {
                "Name": "ServiceName",
                "Value": ECS_SERVICE
            }
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=60,
        Statistics=["Average"]
    )

    datapoints = response.get("Datapoints", [])

    if not datapoints:
        raise HTTPException(
            status_code=503,
            detail=f"No CloudWatch datapoints available for {metric_name}"
        )

    # Select the most recent available datapoint
    latest_datapoint = max(
        datapoints,
        key=lambda point: point["Timestamp"]
    )

    return {
        "value": round(latest_datapoint["Average"], 2),
        "unit": latest_datapoint.get("Unit"),
        "timestamp": latest_datapoint["Timestamp"].isoformat()
    }


# --------------------------------------------------
# 14. Analyze Live ECS Incident
# --------------------------------------------------

@app.get("/analyze-live-incident")
def analyze_live_incident():

    try:

        # Retrieve actual ECS metrics from CloudWatch
        cpu = get_ecs_metric("CPUUtilization")
        memory = get_ecs_metric("MemoryUtilization")

        # Prepare incident information for the analyzer
        incident_data = {
            "incident_id": f"LIVE-{uuid.uuid4().hex[:8]}",
            "incident_type": "Live ECS Monitoring",
            "region": AWS_REGION,
            "service": "ECS",
            "severity": "unknown",

            "metrics": {
                "cpu_utilization": cpu["value"],
                "memory_utilization": memory["value"],

                # These signals are not retrieved from CloudWatch
                # by this endpoint.
                "error_count": 0,
                "unhealthy_targets": 0
            },

            # Application health is not independently checked here.
            "application": {
                "status": "healthy"
            }
        }

        # Analyze the retrieved metric values
        analysis_result = analyze_incident(incident_data)

        # Validate the recommended recovery action
        policy_result = validate_recovery_action(
            analysis_result
        )

        return {
            "project": "AIRA",
            "message": "Live ECS metrics retrieved and analyzed",

            "data_source": "Amazon CloudWatch",

            "aws_details": {
                "region": AWS_REGION,
                "cluster": ECS_CLUSTER,
                "service": ECS_SERVICE
            },

            "live_metrics": {
                "cpu_utilization": cpu,
                "memory_utilization": memory
            },

            "analysis": analysis_result,

            "recovery_policy": policy_result,

            "additional_information": {
                "live_signals_not_collected": [
                    "error_count",
                    "unhealthy_targets",
                    "application_status"
                ],
                "note": (
                    "Only CPU and memory are retrieved as live "
                    "CloudWatch metrics by this endpoint."
                )
            }
        }

    except HTTPException:
        raise

    except ClientError as error:

        error_message = error.response.get(
            "Error", {}
        ).get(
            "Message",
            "Unable to retrieve CloudWatch metrics"
        )

        raise HTTPException(
            status_code=502,
            detail=error_message
        )


# --------------------------------------------------


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
