# Copyright (c) 2026 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0
"""Tests for SemanticProcessor identity reconstruction."""

from openviking.storage.queuefs.add_resource_msg import AddResourceMsg
from openviking.storage.queuefs.semantic_msg import SemanticMsg
from openviking.storage.queuefs.semantic_processor import SemanticProcessor


def test_ctx_from_semantic_msg_preserves_custom_role():
    msg = SemanticMsg(
        uri="viking://resources/doc",
        context_type="resource",
        account_id="acme",
        user_id="alice",
        role="reviewer",
    )

    ctx = SemanticProcessor._ctx_from_semantic_msg(msg)

    assert ctx.account_id == "acme"
    assert ctx.user.user_id == "alice"
    assert str(ctx.role) == "reviewer"


def test_ctx_from_semantic_msg_defaults_empty_role_to_root():
    msg = SemanticMsg(
        uri="viking://resources/doc",
        context_type="resource",
        role="",
    )

    ctx = SemanticProcessor._ctx_from_semantic_msg(msg)

    assert str(ctx.role) == "root"


def test_ctx_from_semantic_msg_preserves_saa_provider_context():
    msg = SemanticMsg(
        uri="viking://resources/doc",
        context_type="resource",
        account_id="acme",
        user_id="alice",
        saa_provider_context={
            "headers": {
                "X-SAA-Service-JWT": "header.payload.signature",
                "X-Caller-Service-Code": "talentana",
            },
        },
    )

    ctx = SemanticProcessor._ctx_from_semantic_msg(msg)

    assert ctx.saa_provider_context is not None
    assert ctx.saa_provider_context.get_header("x-saa-service-jwt") == "header.payload.signature"
    assert ctx.saa_provider_context.get_header("X-Caller-Service-Code") == "talentana"


def test_add_resource_msg_round_trips_saa_provider_context():
    msg = AddResourceMsg(
        task_id="task-1",
        path="https://example.com/doc.pdf",
        root_uri="viking://resources/doc",
        account_id="acme",
        user_id="alice",
        role="user",
        saa_provider_context={
            "headers": {
                "X-SAA-Service-JWT": "header.payload.signature",
                "X-Caller-Service-Code": "talentana",
            },
        },
    )

    restored = AddResourceMsg.from_dict(msg.to_dict())

    assert restored.saa_provider_context == {
        "headers": {
            "X-SAA-Service-JWT": "header.payload.signature",
            "X-Caller-Service-Code": "talentana",
        },
    }
