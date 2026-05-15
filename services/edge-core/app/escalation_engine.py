from app.escalation import EscalationStage


def determine_escalation(score: int) -> tuple[EscalationStage, str]:
    if score <= 20:
        return (
            EscalationStage.SUPPRESS,
            "Suppress expected behaviour and continue monitoring.",
        )

    if score <= 40:
        return (
            EscalationStage.OCCUPANT_AWARENESS,
            "Log irregular activity and keep occupants passively aware.",
        )

    if score <= 65:
        return (
            EscalationStage.VERIFICATION,
            "Request occupant verification.",
        )

    if score <= 85:
        return (
            EscalationStage.HUMAN_MONITORING_PREP,
            "Prepare human monitoring and continue live evaluation.",
        )

    return (
        EscalationStage.EMERGENCY_RESPONSE,
        "Trigger emergency response protocol.",
    )
