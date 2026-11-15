
import json
import os
import urllib.request
import urllib.error
import uuid
from datetime import datetime, timezone

ANALYZER_URL = os.environ.get(
    "ANALYZER_URL",
    "http://aira-alb-879435582.ap-south-1.elb.amazonaws.com/analyze-incident"
)


def lambda_handler(event, context):
    """
    AIRA incident handler.

    Receives an incident, calls the FastAPI analyzer,
    and checks the recovery policy response.

    Does not execute recovery actions yet.
    """

    incident = event.get("incident", event)

    incident.setdefault("incident_id", str(uuid.uuid4()))
    incident.setdefault("region", os.environ.get("AWS_REGION", "ap-south-1"))
    incident.setdefault("service", "aira-api")

    payload = json.dumps(incident).encode("utf-8")

    request = urllib.request.Request(
        ANALYZER_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            result = json.loads(response.read().decode("utf-8"))

        analysis = result.get("analysis", {})
        policy = result.get("recovery_policy", {})

        policy_status = policy.get("status")

        if policy_status == "approved":
            next_step = "recovery_execution_pending"
        elif policy_status == "pending_approval":
            next_step = "awaiting_human_approval"
        else:
            next_step = "no_execution"

        return {
            "incident_id": analysis.get("incident_id"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "analysis": analysis,
            "recovery_policy": policy,
            "workflow_status": next_step,
            "recovery_executed": False
        }

    except urllib.error.HTTPError as error:
        return {
            "statusCode": error.code,
            "error": "Analyzer API returned an HTTP error",
            "details": error.read().decode("utf-8")
        }

    except Exception as error:
        return {
            "statusCode": 500,
            "error": "Incident processing failed",
            "details": str(error)
        }