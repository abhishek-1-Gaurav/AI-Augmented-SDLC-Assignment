"""Fail-closed preflight for explicit policy-bypass and harmful requests."""

import re
from dataclasses import dataclass
from typing import Literal

SafetyReason = Literal[
    "policy_override",
    "sensitive_disclosure",
    "physical_harm",
]

_POLICY_TERM = r"(?:safety|output|rules?|polic(?:y|ies)|instructions?|prompt)"
_OVERRIDE_TERM = r"(?:ignore|disregard|bypass|override|circumvent)"
_POLICY_OVERRIDE = re.compile(
    rf"\b{_OVERRIDE_TERM}\b.{{0,100}}\b{_POLICY_TERM}\b"
    rf"|\b{_POLICY_TERM}\b.{{0,100}}\b{_OVERRIDE_TERM}\b",
    re.IGNORECASE | re.DOTALL,
)
_DISCLOSURE_ACTION = r"(?:disclose|reveal|expose|publish|share|dump|exfiltrate)"
_SENSITIVE_TERM = (
    r"(?:private|personal|confidential|sensitive|account|credential|password|secret)"
)
_SENSITIVE_DISCLOSURE = re.compile(
    rf"\b{_DISCLOSURE_ACTION}\b.{{0,100}}\b{_SENSITIVE_TERM}\b"
    rf"|\b{_SENSITIVE_TERM}\b.{{0,100}}\b{_DISCLOSURE_ACTION}\b",
    re.IGNORECASE | re.DOTALL,
)
_HARM_ACTION = r"(?:harm|hurt|injure|kill|poison|attack)"
_HUMAN_TARGET = r"(?:someone|somebody|person|people|human|another person)"
_PHYSICAL_HARM = re.compile(
    rf"\b{_HARM_ACTION}\b.{{0,60}}\b{_HUMAN_TARGET}\b"
    rf"|\b{_HUMAN_TARGET}\b.{{0,60}}\b{_HARM_ACTION}\b",
    re.IGNORECASE | re.DOTALL,
)


@dataclass(frozen=True)
class RequestSafetyDecision:
    blocked: bool
    reason: SafetyReason | None = None


def assess_request_safety(request: str | None) -> RequestSafetyDecision:
    """Block clear unsafe/bypass signals before sending request text to a model.

    This conservative lexical gate is a defense-in-depth control, not a
    complete content-moderation system.
    """
    if not request:
        return RequestSafetyDecision(blocked=False)
    if _POLICY_OVERRIDE.search(request):
        return RequestSafetyDecision(blocked=True, reason="policy_override")
    if _SENSITIVE_DISCLOSURE.search(request):
        return RequestSafetyDecision(blocked=True, reason="sensitive_disclosure")
    if _PHYSICAL_HARM.search(request):
        return RequestSafetyDecision(blocked=True, reason="physical_harm")
    return RequestSafetyDecision(blocked=False)

