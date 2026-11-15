
"""
AIRA Recovery Policy Validator

Validates incident analysis recommendations before
they are passed to the recovery execution component.
"""

ALLOWED_ACTIONS = {
    "no_action",
    "scale_ecs",
    "replace_unhealthy_tasks",
    "investigate_application_errors"
}

HIGH_RISK_ACTIONS = {
    "scale_ecs",
    "replace_unhealthy_tasks"
}


def validate_recovery_action(analysis):
    """
    Validate a recommended recovery action.

    Returns a structured policy validation result.
    Does not execute any AWS operation.
    """

    if not isinstance(analysis, dict):
        raise ValueError("Analysis must be a dictionary.")

    action = analysis.get("recommended_action")
    severity = analysis.get("severity")
    requires_approval = analysis.get("requires_approval")

    if action not in ALLOWED_ACTIONS:
        return {
            "approved": False,
            "action": action,
            "status": "rejected",
            "reason": "Recovery action is not in the allowed action list."
        }

    if severity not in {"low", "medium", "high"}:
        return {
            "approved": False,
            "action": action,
            "status": "rejected",
            "reason": "Invalid incident severity."
        }

    if not isinstance(requires_approval, bool):
        return {
            "approved": False,
            "action": action,
            "status": "rejected",
            "reason": "Approval requirement must be a boolean value."
        }

    if action in HIGH_RISK_ACTIONS and not requires_approval:
        return {
            "approved": False,
            "action": action,
            "status": "rejected",
            "reason": "High-risk recovery action requires approval."
        }

    if requires_approval:
        return {
            "approved": False,
            "action": action,
            "status": "pending_approval",
            "reason": "Human approval is required before recovery execution."
        }

    return {
        "approved": True,
        "action": action,
        "status": "approved",
        "reason": "Recovery action passed policy validation."
    }
