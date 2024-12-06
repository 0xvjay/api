from datetime import datetime
from typing import Any, List, Union

from pydantic import UUID4, BaseModel, Field

from .constant import Status


class ExportFilter(BaseModel):
    field: str
    value: Union[str, int, float, bool, List[Any], tuple[Any, Any]]
    operator: str = "eq"  # eq, in_, between, gt, lt, contains


class BaseExportSchema(BaseModel):
    file: str | None = None
    status: Status
    user_id: UUID4
    started_at: datetime | None
    finished_at: datetime | None


class ExportCreateSchema(BaseModel):
    model_name: str
    filters: List[ExportFilter] = Field(default_factory=list)
    sort_by: List[str] = Field(default_factory=list)
    file_format: str = "xlsx"  # xlsx, csv, json
    created_by: UUID4 | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "model_name": "User",
                "filters": [
                    {"field": "status", "value": "active", "operator": "eq"},
                    {
                        "field": "created_at",
                        "value": ["2024-01-01", "2024-12-31"],
                        "operator": "between",
                    },
                    {"field": "id", "value": [1, 2, 3], "operator": "in_"},
                ],
                "sort_by": ["-created_at", "email"],
                "file_format": "xlsx",
            }
        }


class ExportOutSchema(BaseExportSchema):
    id: UUID4
