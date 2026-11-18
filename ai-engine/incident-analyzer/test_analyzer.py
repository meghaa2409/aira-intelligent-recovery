
from analyzer import analyze_incident

test_cases = [
    {
        "incident_id": "AIRA-001",
        "incident_type": "application_error",
        "region": "ap-south-1",
        "service": "aira-api",
        "metrics": {
            "cpu_utilization": 45,
            "http_5xx_count": 10,
            "unhealthy_targets": 1
        },
        "application": {
            "health_status": "unhealthy"
        }
    },
    {
        "incident_id": "AIRA-002",
        "incident_type": "high_cpu",
        "region": "ap-south-1",
        "service": "aira-api",
        "metrics": {
            "cpu_utilization": 92,
            "http_5xx_count": 0,
            "unhealthy_targets": 0
        },
        "application": {
            "health_status": "healthy"
        }
    },
    {
        "incident_id": "AIRA-003",
        "incident_type": "application_errors",
        "region": "ap-south-1",
        "service": "aira-api",
        "metrics": {
            "cpu_utilization": 40,
            "http_5xx_count": 15,
            "unhealthy_targets": 0
        },
        "application": {
            "health_status": "healthy"
        }
    },
    {
        "incident_id": "AIRA-004",
        "incident_type": "normal",
        "region": "ap-south-1",
        "service": "aira-api",
        "metrics": {
            "cpu_utilization": 35,
            "http_5xx_count": 0,
            "unhealthy_targets": 0
        },
        "application": {
            "health_status": "healthy"
        }
    }
]

for incident in test_cases:
    result = analyze_incident(incident)

    print("\n" + "=" * 45)
    print("AIRA INCIDENT ANALYSIS")
    print("=" * 45)

    for key, value in result.items():
        print(f"{key}: {value}")
