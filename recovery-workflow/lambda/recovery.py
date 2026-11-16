import json
import os
import boto3
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

REGION = os.environ.get("AWS_REGION", "ap-south-1")
CLUSTER = os.environ.get("ECS_CLUSTER", "aira-cluster")
SERVICE = os.environ.get("ECS_SERVICE", "aira-service")

EXECUTION_ENABLED = (
    os.environ.get("EXECUTION_ENABLED", "false").lower() == "true"
)

HEALTH_CHECK_URL = os.environ.get("HEALTH_CHECK_URL")

ecs = boto3.client("ecs", region_name=REGION)


def check_application_health():

    if not HEALTH_CHECK_URL:
        return "not_configured"

    for attempt in range(5):
        try:
            request = urllib.request.Request(HEALTH_CHECK_URL)

            with urllib.request.urlopen(request, timeout=5) as response:
                if response.status == 200:
                    return "healthy"

        except Exception:
            pass

        time.sleep(5)

    return "unhealthy"


def lambda_handler(event, context):

    start_time = time.monotonic()

    print("Received recovery request:", json.dumps(event))

    action = event.get("action")
    incident_id = event.get("incident_id")

    if action != "scale_ecs" or not incident_id:
        return {
            "status": "rejected",
            "reason": "Valid incident_id and scale_ecs action required.",
            "recovery_executed": False
        }

    desired_count = event.get("desired_count", 2)

    if type(desired_count) is not int or not 1 <= desired_count <= 3:
        return {
            "status": "rejected",
            "reason": "Desired count must be between 1 and 3.",
            "recovery_executed": False
        }

    if event.get("dry_run") is True:
        return {
            "status": "dry_run_success",
            "incident_id": incident_id,
            "action": action,
            "planned_desired_count": desired_count,
            "recovery_executed": False
        }

    if event.get("approved") is not True or not event.get("approved_by"):
        return {
            "status": "awaiting_human_approval",
            "recovery_executed": False
        }

    if not EXECUTION_ENABLED:
        return {
            "status": "execution_disabled",
            "recovery_executed": False
        }

    try:

        ecs.update_service(
            cluster=CLUSTER,
            service=SERVICE,
            desiredCount=desired_count
        )

        ecs.get_waiter("services_stable").wait(
            cluster=CLUSTER,
            services=[SERVICE],
            WaiterConfig={
                "Delay": 15,
                "MaxAttempts": 15
            }
        )

        response = ecs.describe_services(
            cluster=CLUSTER,
            services=[SERVICE]
        )

        service = response["services"][0]

        ecs_stable = (
            service["desiredCount"] == desired_count
            and service["runningCount"] == desired_count
            and service["pendingCount"] == 0
        )

        application_health = (
            check_application_health() if ecs_stable else "not_checked"
        )

        duration = round(time.monotonic() - start_time, 2)

        return {
            "status": "recovery_completed" if ecs_stable else "recovery_unverified",
            "incident_id": incident_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "approved_by": event["approved_by"],
            "action": action,
            "cluster": CLUSTER,
            "service": SERVICE,
            "desired_count": service["desiredCount"],
            "running_count": service["runningCount"],
            "pending_count": service["pendingCount"],
            "ecs_stable": ecs_stable,
            "application_health": application_health,
            "recovery_duration_seconds": duration,
            "recovery_executed": True
        }

    except Exception as error:

        return {
            "status": "recovery_failed",
            "incident_id": incident_id,
            "details": str(error),
            "recovery_executed": False
        }