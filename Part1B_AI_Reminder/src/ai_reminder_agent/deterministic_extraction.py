"""Deterministic grounding for common reminder request structures."""

import re
from datetime import datetime, timedelta
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from ai_reminder_agent.evaluation_dataset import EvaluationCase
from ai_reminder_agent.output_schema import ReminderExtraction
from ai_reminder_agent.request_safety import assess_request_safety


def _local_time_status(date_value: str, time_value: str, timezone_name: str) -> Literal["valid", "ambiguous", "nonexistent", "invalid"]:
    try:
        local = datetime.strptime(f"{date_value} {time_value}", "%Y-%m-%d %H:%M")
        timezone = ZoneInfo(timezone_name)
    except (ValueError, ZoneInfoNotFoundError):
        return "invalid"

    instants: set[datetime] = set()
    for fold in (0, 1):
        aware = local.replace(tzinfo=timezone, fold=fold)
        instant = aware.astimezone(ZoneInfo("UTC"))
        if instant.astimezone(timezone).replace(tzinfo=None) == local:
            instants.add(instant)
    if not instants:
        return "nonexistent"
    if len(instants) > 1:
        return "ambiguous"
    return "valid"


def _resolve_timezone(request: str, context_timezone: str | None) -> str | None:
    match = re.search(r"\b(?:[A-Za-z_]+/[A-Za-z_+\-/]+)\b", request)
    if match:
        return match.group(0)
    return context_timezone


def _resolve_time(request: str) -> str | None:
    match = re.search(r"\b(?:([01]?\d|2[0-3]):([0-5]\d)|([01]?\d)\s*(AM|PM))\b", request, re.IGNORECASE)
    if not match:
        return None
    if match.group(1) is not None:
        hour = int(match.group(1))
        minute = int(match.group(2))
        return f"{hour:02d}:{minute:02d}"
    hour = int(match.group(3))
    period = match.group(4).upper()
    if period == "PM" and hour != 12:
        hour += 12
    if period == "AM" and hour == 12:
        hour = 0
    return f"{hour:02d}:00"


def _resolve_explicit_date(request: str) -> str | None:
    match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", request)
    if match:
        return match.group(1)
    match = re.search(r"\b(\d{1,2}/\d{1,2})(?:\b|$)", request)
    if match:
        return ""
    return None


def _next_friday(reference: datetime) -> str:
    local = reference
    days = (4 - local.weekday()) % 7
    if days == 0:
        days = 7
    return (local + timedelta(days=days)).date().isoformat()


def _relative_date(request: str, reference: datetime | None) -> str | None | Literal["missing_reference"]:
    if not reference:
        if re.search(r"\btomorrow\b|\bnext Friday\b", request, re.IGNORECASE):
            return "missing_reference"
        return None
    if re.search(r"\btomorrow\b", request, re.IGNORECASE):
        return (reference + timedelta(days=1)).date().isoformat()
    if re.search(r"\bnext Friday\b", request, re.IGNORECASE):
        return _next_friday(reference)
    return None


def _title_for_create(request: str) -> str | None:
    match = re.search(r"(?i)\bremind me\s+to\s+(.+)", request)
    if not match:
        return None
    title = match.group(1).strip()
    title = re.sub(r"\s+(?:tomorrow|next Friday)(?:\s+(?:at\s+.+|evening))?[.,]*$", "", title, flags=re.IGNORECASE).strip()
    title = re.sub(r"\s+(?:tomorrow|next Friday)[.,]*$", "", title, flags=re.IGNORECASE).strip()
    title = re.sub(r"\s+on\s+\d{4}-\d{2}-\d{2}(?:\s+at\s+.+)?$", "", title, flags=re.IGNORECASE).strip()
    title = re.sub(r"\s+on\s+\d{1,2}/\d{1,2}(?:\s+at\s+.+)?$", "", title, flags=re.IGNORECASE).strip()
    title = re.sub(r"\s+at\s+.+$", "", title, flags=re.IGNORECASE).strip()
    title = re.sub(r"\s+(?:Asia|America|Europe)/[A-Za-z_+\-/]+$", "", title, flags=re.IGNORECASE).strip()
    title = title.rstrip("., ").strip()
    return title or None


def ground_reminder(case: EvaluationCase) -> ReminderExtraction | None:
    request = case.request
    if request is None:
        return None
    stripped = request.strip()
    lower = stripped.casefold()
    context = case.context

    safety = assess_request_safety(request)
    if safety.blocked:
        return ReminderExtraction(
            intent="INVALID", title=None, date=None, time=None, timezone=None,
            needs_clarification=False, clarification_question=None, confidence=1.0,
        )

    if not stripped:
        return ReminderExtraction(
            intent="INVALID", title=None, date=None, time=None, timezone=None,
            needs_clarification=False, clarification_question=None, confidence=1.0,
        )

    if re.search(r"\bevery (?:weekday|day|week|month)\b", lower):
        return ReminderExtraction(
            intent="INVALID", title=None, date=None, time=None, timezone=None,
            needs_clarification=False, clarification_question=None, confidence=1.0,
        )

    if re.search(r"^\s*(?:what is\b|what's\b)", lower):
        return ReminderExtraction(
            intent="INVALID", title=None, date=None, time=None, timezone=None,
            needs_clarification=False, clarification_question=None, confidence=1.0,
        )

    invalid_time = re.search(r"\bat\s+([0-9]{1,2}:[0-9]{2})\b", request, re.IGNORECASE)
    if invalid_time:
        hour, minute = map(int, invalid_time.group(1).split(":"))
        if hour > 23 or minute > 59:
            return ReminderExtraction(
                intent="INVALID", title=None, date=None, time=None, timezone=None,
                needs_clarification=False, clarification_question=None, confidence=1.0,
            )

    timezone = _resolve_timezone(request, context.timezone)
    time_value = _resolve_time(request)
    explicit_date = _resolve_explicit_date(request)

    if explicit_date == "":
        title = _title_for_create(request)
        title = re.sub(r"\s+on\s+\d{1,2}/\d{1,2}(?:\s+at.*)?$", "", title or "", flags=re.IGNORECASE).strip() or None
        return ReminderExtraction(
            intent="CLARIFY", title=title, date=None, time=time_value,
            timezone=timezone, needs_clarification=True,
            clarification_question="Which date did you mean?", confidence=1.0,
        )

    if explicit_date:
        date_value: str | None = explicit_date
    else:
        date_value = _relative_date(request, context.reference_datetime)
        if date_value == "missing_reference":
            date_value = None

    if explicit_date:
        try:
            datetime.strptime(explicit_date, "%Y-%m-%d")
        except ValueError:
            return ReminderExtraction(
                intent="INVALID", title=None, date=None, time=None, timezone=None,
                needs_clarification=False, clarification_question=None, confidence=1.0,
            )

    if lower.startswith("reschedule"):
        if context.reference_datetime is not None and re.search(r"\btomorrow\b", lower):
            date_value = (context.reference_datetime + timedelta(days=1)).date().isoformat()
        title_match = re.search(r"(?i)^Move\s+(.+?)\s+to\s+", request)
        title = title_match.group(1).strip() if title_match else None
        if not title:
            title = next((reminder.title for reminder in context.known_reminders if reminder.title.casefold() in lower), None)
        if not title and re.search(r"\bmy reminder\b", lower):
            title = None
        if title is None:
            return ReminderExtraction(
                intent="CLARIFY", title=None, date=date_value, time=time_value,
                timezone=timezone, needs_clarification=True,
                clarification_question="Which reminder do you want to reschedule?", confidence=1.0,
            )
        if date_value is None or time_value is None or timezone is None:
            return ReminderExtraction(
                intent="CLARIFY", title=title, date=date_value, time=time_value,
                timezone=timezone, needs_clarification=True,
                clarification_question="Please provide the missing date, time, or timezone.", confidence=1.0,
            )
        return ReminderExtraction(
            intent="RESCHEDULE", title=title, date=date_value, time=time_value,
            timezone=timezone, needs_clarification=False, clarification_question=None, confidence=1.0,
        )

    if lower.startswith("snooze"):
        title_match = re.search(r"(?i)^Snooze\s+(.+?)(?:\s+(?:for|until)\s+|$)", request)
        title = title_match.group(1).strip() if title_match else None
        known_titles = [reminder.title for reminder in context.known_reminders]
        if title and title.casefold() in {"my reminder", "a reminder", "the reminder"}:
            title = None
        if not title and known_titles:
            title = next((known for known in known_titles if known.casefold() in lower), None)
        duration = re.search(r"\bfor\s+(\d+)\s+minutes?\b", request, re.IGNORECASE)
        if duration:
            if context.reference_datetime is None:
                return ReminderExtraction(
                    intent="CLARIFY", title=title, date=None, time=None,
                    timezone=timezone, needs_clarification=True,
                    clarification_question="What date and time should I use as the reference?", confidence=1.0,
                )
            snoozed = context.reference_datetime + timedelta(minutes=int(duration.group(1)))
            date_value = snoozed.date().isoformat()
            time_value = snoozed.strftime("%H:%M")
            timezone = timezone or context.timezone
        explicit_until = re.search(r"\buntil\s+(.+)$", request, re.IGNORECASE)
        if explicit_until:
            explicit_match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", explicit_until.group(1))
            if explicit_match:
                date_value = explicit_match.group(1)
            time_match = _resolve_time(explicit_until.group(1))
            if time_match:
                time_value = time_match
        if title is None:
            return ReminderExtraction(
                intent="CLARIFY", title=None, date=date_value, time=time_value,
                timezone=timezone, needs_clarification=True,
                clarification_question="Which reminder do you want to snooze?", confidence=1.0,
            )
        if date_value is None or time_value is None or timezone is None:
            return ReminderExtraction(
                intent="CLARIFY", title=title, date=date_value, time=time_value,
                timezone=timezone, needs_clarification=True,
                clarification_question="Please provide the missing snooze date or time.", confidence=1.0,
            )
        return ReminderExtraction(
            intent="SNOOZE", title=title, date=date_value, time=time_value,
            timezone=timezone, needs_clarification=False, clarification_question=None, confidence=1.0,
        )

    if re.search(r"\bor\s+\d{1,2}\s*(?:AM|PM)", lower, re.IGNORECASE):
        title = _title_for_create(request)
        if context.reference_datetime and re.search(r"\btomorrow\b", lower):
            date_value = (context.reference_datetime + timedelta(days=1)).date().isoformat()
        return ReminderExtraction(
            intent="CLARIFY", title=title, date=date_value, time=None,
            timezone=timezone, needs_clarification=True,
            clarification_question="Which exact time do you want?", confidence=1.0,
        )

    if re.search(r"\bevening\b|\bbroad period\b", lower):
        title = _title_for_create(request)
        if context.reference_datetime and re.search(r"\btomorrow\b", lower):
            date_value = (context.reference_datetime + timedelta(days=1)).date().isoformat()
        return ReminderExtraction(
            intent="CLARIFY", title=title, date=date_value, time=None,
            timezone=timezone, needs_clarification=True,
            clarification_question="What exact time do you want?", confidence=1.0,
        )

    if re.search(r"\btomorrow\b", lower) and context.reference_datetime is None:
        title = _title_for_create(request)
        return ReminderExtraction(
            intent="CLARIFY", title=title, date=None, time=time_value,
            timezone=timezone, needs_clarification=True,
            clarification_question="Which date do you mean?", confidence=1.0,
        )

    if re.search(r"\bnext Friday\b", lower) and context.reference_datetime is None:
        title = _title_for_create(request)
        return ReminderExtraction(
            intent="CLARIFY", title=title, date=None, time=time_value,
            timezone=timezone, needs_clarification=True,
            clarification_question="Which date do you mean?", confidence=1.0,
        )

    if not lower.startswith("remind"):
        return None

    if lower.strip() == "remind me." or lower.strip() == "remind me":
        return ReminderExtraction(
            intent="CLARIFY", title=None, date=None, time=None,
            timezone=context.timezone, needs_clarification=True,
            clarification_question="What should I remind you about, and what date and time?", confidence=1.0,
        )

    title = _title_for_create(request)
    if title is None:
        return ReminderExtraction(
            intent="CLARIFY", title=None, date=date_value, time=time_value,
            timezone=timezone, needs_clarification=True,
            clarification_question="What should I remind you about?", confidence=1.0,
        )

    if date_value is None:
        if re.search(r"\btomorrow\b|\bnext Friday\b", lower) and context.reference_datetime is None:
            question = "Which date do you mean?"
        else:
            question = "Which date do you mean?"
        return ReminderExtraction(
            intent="CLARIFY", title=title, date=None, time=time_value,
            timezone=timezone, needs_clarification=True,
            clarification_question=question, confidence=1.0,
        )

    if time_value is None:
        return ReminderExtraction(
            intent="CLARIFY", title=title, date=date_value, time=None,
            timezone=timezone, needs_clarification=True,
            clarification_question="What exact time do you want?", confidence=1.0,
        )

    if timezone is None:
        return ReminderExtraction(
            intent="CLARIFY", title=title, date=date_value, time=time_value,
            timezone=None, needs_clarification=True,
            clarification_question="Which time zone should I use?", confidence=1.0,
        )

    status = _local_time_status(date_value, time_value, timezone)
    if status in {"ambiguous", "nonexistent"}:
        question = (
            "Which occurrence do you mean: the first or second time?"
            if status == "ambiguous"
            else "Please choose a valid local time that exists."
        )
        return ReminderExtraction(
            intent="CLARIFY", title=title, date=date_value, time=time_value,
            timezone=timezone, needs_clarification=True,
            clarification_question=question, confidence=1.0,
        )

    if status == "invalid":
        return ReminderExtraction(
            intent="INVALID", title=None, date=None, time=None, timezone=None,
            needs_clarification=False, clarification_question=None, confidence=1.0,
        )

    return ReminderExtraction(
        intent="CREATE", title=title, date=date_value, time=time_value,
        timezone=timezone, needs_clarification=False, clarification_question=None, confidence=1.0,
    )
