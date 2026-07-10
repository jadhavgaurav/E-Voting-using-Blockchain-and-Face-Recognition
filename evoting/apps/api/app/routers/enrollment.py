"""Face enrollment endpoints (voter auth required)."""

from __future__ import annotations

from fastapi import APIRouter, File, UploadFile

from app.core.deps import CurrentVoter, DbSession
from app.core.errors import ValidationError
from app.schemas import EnrollmentStatusOut
from app.services import enrollment

router = APIRouter(prefix="/enrollment", tags=["enrollment"])

_MAX_IMAGE_BYTES = 5 * 1024 * 1024


@router.post("/face", response_model=EnrollmentStatusOut)
async def enroll(
    voter: CurrentVoter, db: DbSession, file: UploadFile = File(...)
) -> EnrollmentStatusOut:
    data = await file.read()
    if len(data) > _MAX_IMAGE_BYTES:
        raise ValidationError("Image too large", code="IMAGE_TOO_LARGE")
    template = await enrollment.enroll_face(db, voter, data)
    return EnrollmentStatusOut(enrolled=True, algorithm_version=template.algorithm_version)


@router.get("/status", response_model=EnrollmentStatusOut)
async def status(voter: CurrentVoter, db: DbSession) -> EnrollmentStatusOut:
    template = await enrollment.get_template(db, voter)
    if template is None:
        return EnrollmentStatusOut(enrolled=False)
    return EnrollmentStatusOut(enrolled=True, algorithm_version=template.algorithm_version)
