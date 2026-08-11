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
