
from datetime import datetime, timezone, timedelta
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
# 4. AWS Configuration
# --------------------------------------------------

AWS_REGION = "ap-south-1"

ECS_CLUSTER = "aira-cluster"
ECS_SERVICE = "aira-service"

STATE_MACHINE_ARN = os.getenv(
    "AIRA_STATE_MACHINE_ARN",
    "arn:aws:states:ap-south-1:016279724502:stateMachine:aira-recovery-workflow"
)

# Step Functions client
sfn_client = boto3.client(
    "stepfunctions",
    region_name=AWS_REGION
)

# CloudWatch client
cloudwatch_client = boto3.client(
    "cloudwatch",
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
# 12. Analyze Manually Supplied Incident
# --------------------------------------------------

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


# --------------------------------------------------
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
# 15. Start Recovery Workflow
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
            "Message",
            "Unable to start recovery workflow"
        )

        raise HTTPException(
            status_code=500,
            detail=error_message
        )


# --------------------------------------------------
# 16. Recovery Approval Endpoint
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
# 17. Recovery Rejection Endpoint
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
