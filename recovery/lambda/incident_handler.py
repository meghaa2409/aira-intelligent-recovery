
import json
import os
import urllib.request
import urllib.error
import uuid
import boto3

from datetime import datetime, timezone, timedelta


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

ANALYZER_URL = os.environ.get(
    "ANALYZER_URL",
    "http://aira-alb-879435582.ap-south-1.elb.amazonaws.com/analyze-incident"
)

DEFAULT_REGION = os.environ.get("AWS_REGION", "ap-south-1")
CLUSTER_NAME = os.environ.get("ECS_CLUSTER", "aira-cluster")
SERVICE_NAME = os.environ.get("ECS_SERVICE", "aira-service")


# --------------------------------------------------
# RETRIEVE ACTUAL ECS CPU METRIC
# --------------------------------------------------

def get_ecs_cpu_utilization(region):

    cloudwatch = boto3.client(
        "cloudwatch",
        region_name=region
    )

    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(minutes=15)

    response = cloudwatch.get_metric_statistics(
        Namespace="AWS/ECS",
        MetricName="CPUUtilization",
        Dimensions=[
            {
                "Name": "ClusterName",
                "Value": CLUSTER_NAME
            },
            {
                "Name": "ServiceName",
                "Value": SERVICE_NAME
            }
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=300,
        Statistics=["Average"]
    )

    datapoints = response.get("Datapoints", [])

    if not datapoints:
        return None

    latest = max(
        datapoints,
        key=lambda point: point["Timestamp"]
    )

    return round(latest["Average"], 2)


# --------------------------------------------------
# CALL FASTAPI ANALYZER
# --------------------------------------------------

def call_analyzer(incident):

    payload = json.dumps(incident).encode("utf-8")

    request = urllib.request.Request(
        ANALYZER_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


# --------------------------------------------------
# EXTRACT CLOUDWATCH ALARM
# --------------------------------------------------

def extract_alarm_event(event):

    detail = event.get("detail", {})
    state = detail.get("state", {})

    return {
        "alarm_name": detail.get("alarmName", "unknown-alarm"),
        "alarm_state": state.get("value"),
        "reason": state.get("reason", "No reason provided"),
        "region": event.get("region", DEFAULT_REGION),
        "event_id": event.get("id", str(uuid.uuid4()))
    }


# --------------------------------------------------
# MAIN LAMBDA HANDLER
# --------------------------------------------------

def lambda_handler(event, context):

    alarm = None

    try:

        # Handle CloudWatch alarm events
        if event.get("source") == "aws.cloudwatch":

            alarm = extract_alarm_event(event)

            if alarm["alarm_state"] != "ALARM":

                return {
                    "status": "ignored",
                    "reason": "Alarm is not in ALARM state",
                    "alarm": alarm,
                    "recovery_executed": False
                }

            # Retrieve actual CPU metric
            cpu = get_ecs_cpu_utilization(alarm["region"])

            # Never invent a metric value
            if cpu is None:

                return {
                    "status": "metrics_unavailable",
                    "alarm": alarm,
                    "reason": "No ECS CPU datapoints found in CloudWatch.",
                    "recovery_executed": False
                }

            incident = {
                "incident_id": alarm["event_id"],
                "incident_type": "high_cpu",
                "region": alarm["region"],
                "service": SERVICE_NAME,
                "severity": "high",
                "metrics": {
                    "cpu_utilization": cpu,
                    "http_5xx_count": 0,
                    "unhealthy_targets": 0
                },
                "application": {
                    "health_status": "unknown"
                }
            }

        else:

            # Support existing local incident tests
            incident = event.get("incident", event)

            incident.setdefault("incident_id", str(uuid.uuid4()))
            incident.setdefault("region", DEFAULT_REGION)
            incident.setdefault("service", SERVICE_NAME)

        # Validate incident structure
        required_fields = [
            "incident_id",
            "incident_type",
            "region",
            "service",
            "severity",
            "metrics",
            "application"
        ]

        missing = [
            field for field in required_fields
            if field not in incident
        ]

        if missing:

            return {
                "status": "invalid_incident",
                "missing_fields": missing,
                "recovery_executed": False
            }

        # Send incident to analyzer
        result = call_analyzer(incident)

        analysis = result.get("analysis", {})
        policy = result.get("recovery_policy", {})

        policy_status = policy.get("status")

        if policy_status == "approved":
            workflow_status = "recovery_execution_pending"

        elif policy_status == "pending_approval":
            workflow_status = "awaiting_human_approval"

        elif policy_status == "rejected":
            workflow_status = "recovery_rejected"

        else:
            workflow_status = "no_execution"

        return {
            "incident_id": analysis.get("incident_id"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "alarm": alarm,
            "analysis": analysis,
            "recovery_policy": policy,
            "workflow_status": workflow_status,
            "recovery_executed": False
        }

    except urllib.error.HTTPError as error:

        return {
            "status": "analyzer_http_error",
            "statusCode": error.code,
            "details": error.read().decode("utf-8"),
            "recovery_executed": False
        }

    except urllib.error.URLError as error:

        return {
            "status": "analyzer_connection_error",
            "details": str(error),
            "recovery_executed": False
        }

    except Exception as error:

        return {
            "status": "incident_processing_failed",
            "details": str(error),
            "recovery_executed": False
        }