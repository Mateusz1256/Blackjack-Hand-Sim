"""Preset API routes."""

from fastapi import APIRouter, Depends, HTTPException, Response, status

from blackjack_api.dependencies import get_preset_repository
from blackjack_api.repositories import PresetRecord, PresetRepository
from blackjack_api.schemas.presets import (
    PresetDuplicateRequest,
    PresetImportRequest,
    PresetListResponse,
    PresetResponse,
)
from blackjack_simulator.presets import preset_from_yaml
from blackjack_simulator.presets.model import Preset, PresetMetadata

router = APIRouter(prefix="/presets")
PresetRepositoryDependency = Depends(get_preset_repository)


@router.get("", response_model=PresetListResponse)
def list_presets(
    category: str | None = None,
    repository: PresetRepository = PresetRepositoryDependency,
) -> PresetListResponse:
    return PresetListResponse(
        presets=[
            _preset_response(record) for record in repository.list(category=category)
        ],
    )


@router.get("/{preset_id}", response_model=PresetResponse)
def get_preset(
    preset_id: str,
    repository: PresetRepository = PresetRepositoryDependency,
) -> PresetResponse:
    record = repository.get(preset_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="preset not found",
        )
    return _preset_response(record)


@router.post(
    "/import",
    response_model=PresetResponse,
    status_code=status.HTTP_201_CREATED,
)
def import_preset(
    request: PresetImportRequest,
    repository: PresetRepository = PresetRepositoryDependency,
) -> PresetResponse:
    try:
        preset = preset_from_yaml(request.preset_text)
        if preset.metadata.read_only:
            preset = _copy_preset(
                preset,
                preset_id=f"{preset.metadata.id}-imported",
                name=f"{preset.metadata.name} imported",
            )
        return _preset_response(repository.upsert(preset))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.post(
    "/{preset_id}/duplicate",
    response_model=PresetResponse,
    status_code=status.HTTP_201_CREATED,
)
def duplicate_preset(
    preset_id: str,
    request: PresetDuplicateRequest,
    repository: PresetRepository = PresetRepositoryDependency,
) -> PresetResponse:
    source = repository.get(preset_id)
    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="preset not found",
        )
    try:
        preset = _copy_preset(source.preset(), preset_id=request.id, name=request.name)
        return _preset_response(repository.upsert(preset))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get("/{preset_id}/export")
def export_preset(
    preset_id: str,
    repository: PresetRepository = PresetRepositoryDependency,
) -> Response:
    record = repository.get(preset_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="preset not found",
        )
    return Response(content=record.config_text, media_type="application/x-yaml")


@router.delete("/{preset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_preset(
    preset_id: str,
    repository: PresetRepository = PresetRepositoryDependency,
) -> Response:
    try:
        deleted = repository.delete(preset_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="preset not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _copy_preset(preset: Preset, *, preset_id: str, name: str) -> Preset:
    metadata = PresetMetadata(
        id=preset_id,
        name=name,
        description=preset.metadata.description,
        category=preset.metadata.category,
        tags=preset.metadata.tags,
        source="user",
        version=preset.metadata.version,
        read_only=False,
    )
    return Preset(metadata=metadata, configuration=preset.configuration)


def _preset_response(record: PresetRecord) -> PresetResponse:
    return PresetResponse(
        id=record.id,
        name=record.name,
        metadata=record.metadata(),
        config_text=record.config_text,
        read_only=record.read_only,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )
