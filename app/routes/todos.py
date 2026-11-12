"""CRUD route handlers for the To-Do API."""
from datetime import datetime, timezone
from typing import List, Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, Query, status
from pymongo import ReturnDocument

from app.database import get_collection
from app.models import MessageResponse, TodoCreate, TodoResponse, TodoStatus, TodoUpdate

router = APIRouter(prefix="/api/todos", tags=["Todos"])


# ---------- helpers ----------
def parse_object_id(todo_id: str) -> ObjectId:
    """Convert a string to ObjectId or raise 400 for invalid formats."""
    try:
        return ObjectId(todo_id)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'{todo_id}' is not a valid ObjectId (expected 24-character hex string).",
        )


def to_response(doc: dict) -> TodoResponse:
    """Map a MongoDB document (_id: ObjectId) to the API response model (id: str)."""
    return TodoResponse(
        id=str(doc["_id"]),
        title=doc["title"],
        description=doc.get("description"),
        status=doc.get("status", TodoStatus.pending.value),
        created_at=doc["created_at"],
    )


def not_found(todo_id: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Todo with id '{todo_id}' not found.",
    )


# ---------- routes ----------
# These are plain `def` handlers on purpose: PyMongo is synchronous, so FastAPI
# runs them in a worker thread pool instead of blocking the event loop.

@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(payload: TodoCreate):
    doc = {
        "title": payload.title,
        "description": payload.description,
        "status": payload.status.value,
        "created_at": datetime.now(timezone.utc),
    }
    result = get_collection().insert_one(doc)
    doc["_id"] = result.inserted_id
    return to_response(doc)


@router.get("", response_model=List[TodoResponse], status_code=status.HTTP_200_OK)
def list_todos(
    status_filter: Optional[TodoStatus] = Query(None, alias="status", description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    query = {"status": status_filter.value} if status_filter else {}
    cursor = get_collection().find(query).sort("created_at", -1).skip(skip).limit(limit)
    return [to_response(doc) for doc in cursor]


@router.get("/{todo_id}", response_model=TodoResponse, status_code=status.HTTP_200_OK)
def get_todo(todo_id: str):
    doc = get_collection().find_one({"_id": parse_object_id(todo_id)})
    if doc is None:
        raise not_found(todo_id)
    return to_response(doc)


@router.put("/{todo_id}", response_model=TodoResponse, status_code=status.HTTP_200_OK)
def update_todo(todo_id: str, payload: TodoUpdate):
    oid = parse_object_id(todo_id)

    # Only update fields the client actually sent. `mode="json"` turns the enum into a plain string.
    changes = payload.model_dump(mode="json", exclude_unset=True)
    if changes.get("status") is None:
        changes.pop("status", None)  # explicit null status -> keep the current one

    doc = get_collection().find_one_and_update(
        {"_id": oid},
        {"$set": changes},
        return_document=ReturnDocument.AFTER,
    )
    if doc is None:
        raise not_found(todo_id)
    return to_response(doc)


@router.delete("/{todo_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
def delete_todo(todo_id: str):
    result = get_collection().delete_one({"_id": parse_object_id(todo_id)})
    if result.deleted_count == 0:
        raise not_found(todo_id)
    return MessageResponse(message="Todo deleted successfully", id=todo_id)