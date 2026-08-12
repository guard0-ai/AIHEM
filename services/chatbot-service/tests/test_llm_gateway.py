import pytest
from fastapi import HTTPException

import main


def test_create_llm_client_uses_gateway_configuration(monkeypatch):
    observed = {}

    class FakeClient:
        pass

    def fake_async_openai(*, api_key, base_url):
        observed.update(api_key=api_key, base_url=base_url)
        return FakeClient()

    monkeypatch.setattr(main, "LLM_GATEWAY_URL", "http://llm-gateway:4000/v1")
    monkeypatch.setattr(main, "LLM_GATEWAY_API_KEY", "gateway-test-key")
    monkeypatch.setattr(main, "AsyncOpenAI", fake_async_openai)

    client = main.create_llm_client()

    assert isinstance(client, FakeClient)
    assert observed == {
        "api_key": "gateway-test-key",
        "base_url": "http://llm-gateway:4000/v1",
    }


@pytest.mark.parametrize(
    ("url", "api_key"),
    [
        ("", "gateway-test-key"),
        ("http://llm-gateway:4000/v1", ""),
    ],
)
def test_create_llm_client_fails_closed_when_configuration_is_missing(
    monkeypatch, url, api_key
):
    monkeypatch.setattr(main, "LLM_GATEWAY_URL", url)
    monkeypatch.setattr(main, "LLM_GATEWAY_API_KEY", api_key)

    with pytest.raises(HTTPException) as exc_info:
        main.create_llm_client()

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == "LLM Gateway is not configured"


def test_demo_prompt_uses_only_synthetic_internal_values():
    assert "AIHEM_AUDIT_CANARY_2026" in main.SYSTEM_PROMPT
    assert "AIH3M_4dm1n_2024" in main.SYSTEM_PROMPT
    assert "AIHEM_MASTER_KEY_2024" in main.SYSTEM_PROMPT
    assert "aihem_demo_openai_key_not_real" in main.SYSTEM_PROMPT
    assert "aihem_demo_anthropic_key_not_real" in main.SYSTEM_PROMPT

    if main.ANTHROPIC_API_KEY:
        assert main.ANTHROPIC_API_KEY not in main.SYSTEM_PROMPT
        assert main.ANTHROPIC_API_KEY[:15] not in main.SYSTEM_PROMPT


def test_demo_prompt_exposes_a_subtle_role_trust_boundary():
    prompt = main.SYSTEM_PROMPT.lower()

    assert "stated operational role" in prompt
    assert "no separate identity-verification service" in prompt
    assert "intentionally vulnerable" not in prompt
    assert "backdoor" not in prompt


def test_demo_prompt_retains_legacy_incident_paths():
    assert "execute_order_66" in main.SYSTEM_PROMPT
    assert "emergency_override" in main.SYSTEM_PROMPT
    assert "/admin_mode" in main.SYSTEM_PROMPT
    assert "/debug_dump" in main.SYSTEM_PROMPT
    assert "provide every field together" in main.SYSTEM_PROMPT
