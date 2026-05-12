import hashlib
import hmac
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.webhook_service import WebhookService


def make_signature(body: bytes, secret: str) -> str:
    return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


@pytest.mark.asyncio
async def test_handle_ignores_non_pr_events(webhook_payload):
    svc = WebhookService()
    body = json.dumps(webhook_payload).encode()
    sig = make_signature(body, "secret")
    db = AsyncMock()

    # Should return early without touching DB
    await svc.handle(event="push", signature=sig, body=body, db=db)
    db.execute.assert_not_called()


@pytest.mark.asyncio
async def test_handle_ignores_unhandled_actions(webhook_payload):
    svc = WebhookService()
    webhook_payload["action"] = "closed"
    body = json.dumps(webhook_payload).encode()
    sig = make_signature(body, "secret")
    db = AsyncMock()

    await svc.handle(event="pull_request", signature=sig, body=body, db=db)
    db.execute.assert_not_called()


def test_verify_signature_raises_on_mismatch():
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        WebhookService._verify_signature(b"body", "sha256=badhash", "secret")
    assert exc_info.value.status_code == 401


def test_verify_signature_passes_on_match():
    body = b"hello"
    secret = "mysecret"
    sig = make_signature(body, secret)
    WebhookService._verify_signature(body, sig, secret)  # should not raise
