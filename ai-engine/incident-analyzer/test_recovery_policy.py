
from recovery_policy import validate_recovery_action

test_cases = [
    {
        "incident_id": "AIRA-007",
        "severity": "low",
        "recommended_action": "no_action",
        "requires_approval": False
    },
    {
        "incident_id": "AIRA-008",
        "severity": "high",
        "recommended_action": "scale_ecs",
        "requires_approval": True
    },
    {
        "incident_id": "AIRA-009",
        "severity": "high",
        "recommended_action": "replace_unhealthy_tasks",
        "requires_approval": True
    },
    {
        "incident_id": "AIRA-010",
        "severity": "high",
        "recommended_action": "delete_database",
        "requires_approval": True
    },
    {
        "incident_id": "AIRA-011",
        "severity": "high",
        "recommended_action": "scale_ecs",
        "requires_approval": False
    }
]

for incident in test_cases:
    result = validate_recovery_action(incident)

    print("\n" + "=" * 45)
    print("AIRA RECOVERY POLICY TEST")
    print("=" * 45)
    print("Incident ID:", incident["incident_id"])

    for key, value in result.items():
        print(f"{key}: {value}")
