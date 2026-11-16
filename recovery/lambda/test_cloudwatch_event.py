
import json
from unittest.mock import patch

from incident_handler import lambda_handler


event = {
    "version": "0",
    "id": "aira-test-alarm-001",
    "source": "aws.cloudwatch",
    "detail-type": "CloudWatch Alarm State Change",
    "region": "ap-south-1",
    "detail": {
        "alarmName": "aira-high-cpu-alarm",
        "state": {
            "value": "ALARM",
            "reason": "CPU exceeded threshold"
        },
        "previousState": {
            "value": "OK"
        }
    }
}


# This test currently checks event recognition.
# The metric lookup will be added in the next update.

with patch(
     "incident_handler.get_ecs_cpu_utilization",
    return_value=92.0
), patch(
    "incident_handler.call_analyzer"
) as mock_analyzer:

    mock_analyzer.return_value = {
        "analysis": {
            "incident_id": "aira-test-alarm-001",
            "recommended_action": "scale_ecs"
        },
        "recovery_policy": {
            "approved": False,
            "action": "scale_ecs",
            "status": "pending_approval"
        }
    }

    result = lambda_handler(event, None)

    print(json.dumps(result, indent=4))

    assert result["workflow_status"] == "awaiting_human_approval"
    assert result["recovery_executed"] is False
    assert result["alarm"]["alarm_state"] == "ALARM"

    print("\nCloudWatch event test PASSED!")