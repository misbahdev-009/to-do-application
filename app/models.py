"""Pydantic schemas for request validation and response serialization."""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class TodoStatus(str, Enum):
    pending = "pending"
    completed = "completed"


def _clean_title(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("title must not be empty")
    return value


class TodoCreate(BaseModel):
    title: str = Field(..., max_length=200, examples=["Buy groceries"])
    description: Optional[str] = Field(default=None, max_length=1000)
    status: TodoStatus = TodoStatus.pending

    _validate_title = field_validator("title")(_clean_title)


class TodoUpdate(BaseModel):
    """PUT payload: title is required; other fields are only changed if sent."""
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[TodoStatus] = None

    _validate_title = field_validator("title")(_clean_title)


class TodoResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    status: TodoStatus
    created_at: datetime  # serialized as ISO 8601 UTC, e.g. 2026-11-12T10:30:00Z


class MessageResponse(BaseModel):
    message: str
    id: str