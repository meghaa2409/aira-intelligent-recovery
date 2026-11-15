
import json
from incident_handler import lambda_handler

with open("../../monitoring/eventbridge/test_alarm_event.json") as file:
    event = json.load(file)

# Convert the simulated alarm into an incident
alarm = event["detail"]

incident_event = {
    "incident": {
        "incident_id": event["id"],
        "incident_type": "high_cpu",
        "region": event["region"],
        "service": "aira-api",
        "severity": "high",
        "metrics": {
            "cpu_utilization": 92,
            "http_5xx_count": 0,
            "unhealthy_targets": 0
        },
        "application": {
            "health_status": "healthy"
        }
    }
}

result = lambda_handler(incident_event, None)

print(json.dumps(result, indent=4))