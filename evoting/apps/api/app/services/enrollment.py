"""Face enrollment: obtain an embedding from the biometrics service, store encrypted."""

from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.biometrics_client import get_biometrics_client
from app.config import get_settings
from app.core import crypto
from app.db.models import EnrollmentTemplate, Voter


def _encode(vector: list[float]) -> bytes:
    settings = get_settings()
    return crypto.encrypt_bytes(json.dumps(vector).encode(), settings.data_encryption_key)


def decode_template(template: EnrollmentTemplate) -> list[float]:
    settings = get_settings()
    raw = crypto.decrypt_bytes(template.template_encrypted, settings.data_encryption_key)
    return [float(x) for x in json.loads(raw)]


async def enroll_face(db: AsyncSession, voter: Voter, image_bytes: bytes) -> EnrollmentTemplate:
    embedding = await get_biometrics_client().embed(image_bytes)

    existing = await db.scalar(
        select(EnrollmentTemplate).where(EnrollmentTemplate.voter_id == voter.id)
    )
    if existing is not None:
        existing.template_encrypted = _encode(embedding.vector)
        existing.algorithm_version = embedding.algorithm_version
        await db.flush()
        return existing

    template = EnrollmentTemplate(
        voter_id=voter.id,
        template_encrypted=_encode(embedding.vector),
        algorithm_version=embedding.algorithm_version,
    )
    db.add(template)
    await db.flush()
    return template


async def get_template(db: AsyncSession, voter: Voter) -> EnrollmentTemplate | None:
    template: EnrollmentTemplate | None = await db.scalar(
        select(EnrollmentTemplate).where(EnrollmentTemplate.voter_id == voter.id)
    )
    return template
