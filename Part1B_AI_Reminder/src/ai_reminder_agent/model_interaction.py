"""Model call orchestration, independent of provider SDKs."""

from typing import Any

from ai_reminder_agent.evaluation_dataset import EvaluationCase
from ai_reminder_agent.output_schema import ReminderExtraction
from ai_reminder_agent.prompt_templates import SYSTEM_INSTRUCTIONS, render_prompt
from ai_reminder_agent.providers.protocol import ModelProvider, ProviderResponse
from ai_reminder_agent.request_safety import assess_request_safety


def output_json_schema() -> dict[str, Any]:
    schema = ReminderExtraction.model_json_schema()
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    return schema


def request_model_output(
    case: EvaluationCase,
    provider: ModelProvider,
    provider_settings: dict[str, Any] | None = None,
) -> ProviderResponse:
    if case.request is None:
        raise ValueError("Schema-only evaluation cases do not call a model provider.")
    safety_decision = assess_request_safety(case.request)
    if safety_decision.blocked:
        return ProviderResponse(
            raw_text=(
                '{"intent":"INVALID","title":null,"date":null,"time":null,'
                '"timezone":null,"needs_clarification":false,'
                '"clarification_question":null,"confidence":1.0}'
            ),
            provider="local_safety_filter",
            model=safety_decision.reason or "blocked",
        )
    schema = output_json_schema()
    context = case.context.model_dump(mode="json")
    prompt = render_prompt(request=case.request, context=context, schema=schema)
    settings = dict(provider_settings or {})
    settings["case_id"] = case.case_id
    return provider.generate(
        request=case.request,
        system_prompt=SYSTEM_INSTRUCTIONS,
        prompt=prompt,
        schema=schema,
        settings=settings,
    )

