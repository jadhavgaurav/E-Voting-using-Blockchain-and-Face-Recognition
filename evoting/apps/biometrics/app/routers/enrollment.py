"""Enrollment endpoint: turn an image into a face embedding."""

from __future__ import annotations

import base64
import binascii

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import ValidationError

from app.config import get_settings
from app.embedders import get_embedder
from app.schemas import EmbedJsonRequest, EmbedResponse
from app.security import require_internal_token

router = APIRouter(
    prefix="/enrollment",
    tags=["enrollment"],
    dependencies=[Depends(require_internal_token)],
)

_UNPROCESSABLE = status.HTTP_422_UNPROCESSABLE_ENTITY


def _decode_b64(image_b64: str) -> bytes:
    try:
        return base64.b64decode(image_b64, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(
            status_code=_UNPROCESSABLE, detail=f"invalid base64 image: {exc}"
        ) from exc


async def _extract_image_bytes(request: Request) -> bytes:
    """Read image bytes from either a multipart upload or a JSON body."""
    content_type = request.headers.get("content-type", "")

    if content_type.startswith("multipart/form-data"):
        form = await request.form()
        upload = form.get("file")
        if upload is None or isinstance(upload, str):
            raise HTTPException(status_code=_UNPROCESSABLE, detail="missing multipart 'file' field")
        return await upload.read()

    # Fall back to JSON {image_b64}.
    try:
        body = await request.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=_UNPROCESSABLE,
            detail="provide either a multipart 'file' or JSON 'image_b64'",
        ) from exc
    try:
        payload = EmbedJsonRequest.model_validate(body)
    except ValidationError as exc:
        raise HTTPException(status_code=_UNPROCESSABLE, detail=exc.errors()) from exc
    return _decode_b64(payload.image_b64)


@router.post("/embed", response_model=EmbedResponse)
async def embed(request: Request) -> EmbedResponse:
    """Return an L2-normalized embedding for the supplied image.

    Accepts either a multipart ``file`` upload or a JSON body ``{image_b64}``.
    Domain errors (NoFaceDetected / MultipleFacesDetected) bubble up to the
    central handler in ``app.main`` and render as a 422 envelope with a code.
    """
    image_bytes = await _extract_image_bytes(request)

    settings = get_settings()
    embedder = get_embedder(settings)
    vector = embedder.embed(image_bytes)
    return EmbedResponse(embedding=vector, algorithm_version=embedder.algorithm_version)
