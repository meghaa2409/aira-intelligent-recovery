
def analyze_incident(incident):
    """
    Analyze an AWS application incident and recommend
    a predefined recovery action using rule-based logic.
    """

    if not isinstance(incident, dict):
        raise ValueError("Incident data must be a dictionary.")

    metrics = incident.get("metrics", {})
    application = incident.get("application", {})

    if not isinstance(metrics, dict):
        raise ValueError("Metrics must be a dictionary.")

    if not isinstance(application, dict):
        raise ValueError("Application data must be a dictionary.")

    cpu = metrics.get("cpu_utilization", 0)
    errors = metrics.get("http_5xx_count", 0)
    unhealthy_targets = metrics.get("unhealthy_targets", 0)
    health_status = application.get("health_status", "unknown")

    # Validate CPU utilization
    if isinstance(cpu, bool) or not isinstance(cpu, (int, float)) or not 0 <= cpu <= 100:
        raise ValueError("CPU utilization must be between 0 and 100.")

    # Validate HTTP errors
    if isinstance(errors, bool) or not isinstance(errors, int) or errors < 0:
        raise ValueError("HTTP 5xx count must be a non-negative integer.")

    # Validate unhealthy targets
    if isinstance(unhealthy_targets, bool) or not isinstance(unhealthy_targets, int) or unhealthy_targets < 0:
        raise ValueError("Unhealthy targets must be a non-negative integer.")

    # Validate application health
    if health_status not in ["healthy", "unhealthy", "unknown"]:
        raise ValueError("Invalid application health status.")

    severity = "low"
    action = "no_action"
    reason = "Application metrics are within acceptable limits."
    requires_approval = False
    detected_signals = []

    # Rule 1: Unhealthy application or targets
    if health_status == "unhealthy" or unhealthy_targets > 0:
        severity = "high"
        action = "replace_unhealthy_tasks"
        reason = (
            "Application health check or target health "
            "indicates a failure."
        )
        requires_approval = True

        if health_status == "unhealthy":
            detected_signals.append("Application health is unhealthy.")

        if unhealthy_targets > 0:
            detected_signals.append(
                f"{unhealthy_targets} unhealthy target(s) detected."
            )

    # Rule 2: High CPU utilization
    elif cpu >= 80:
        severity = "high"
        action = "scale_ecs"
        reason = f"High CPU utilization detected: {cpu}%."
        requires_approval = True
        detected_signals.append(
            f"CPU utilization exceeded the 80% threshold: {cpu}%."
        )

    # Rule 3: HTTP 5xx errors
    elif errors >= 10:
        severity = "medium"
        action = "investigate_application_errors"
        reason = f"Elevated HTTP 5xx errors detected: {errors}."
        requires_approval = True
        detected_signals.append(
            f"HTTP 5xx error count reached {errors}."
        )

    else:
        detected_signals.append(
            "No critical incident signals detected."
        )

    # Incident summary
    summary = (
        f"CPU: {cpu}%, HTTP 5xx errors: {errors}, "
        f"Unhealthy targets: {unhealthy_targets}, "
        f"Application health: {health_status}"
    )

    return {
        "incident_id": incident.get("incident_id", "UNKNOWN"),
        "incident_type": incident.get("incident_type", "unknown"),
        "severity": severity,
        "incident_summary": summary,
        "detected_signals": detected_signals,
        "recommended_action": action,
        "reason": reason,
        "requires_approval": requires_approval,
        "analysis_engine": "rule_based",
        "recovery_safety_note": (
            "The recommended action must be validated against "
            "AIRA recovery policies before execution."
        )
    }
