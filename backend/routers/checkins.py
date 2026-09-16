from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, Query
from pymongo import ReturnDocument

from core.database import get_database
from core.security import current_user_id
from schemas import CheckInIn, CheckInOut
from services.twin_engine import serialize_checkin

router = APIRouter()


@router.post("", response_model=CheckInOut)
def save_checkin(payload: CheckInIn, user_id: str = Depends(current_user_id)):
    now = datetime.now(timezone.utc)
    recorded_on = payload.recorded_on.isoformat()
    document = {**payload.model_dump(), "recorded_on": recorded_on, "user_id": ObjectId(user_id), "updated_at": now}
    saved = get_database().checkins.find_one_and_update(
        {"user_id": ObjectId(user_id), "recorded_on": recorded_on},
        {"$set": document, "$setOnInsert": {"created_at": now}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return serialize_checkin(saved)


@router.get("", response_model=list[CheckInOut])
def list_checkins(limit: int = Query(default=30, ge=1, le=365), user_id: str = Depends(current_user_id)):
    rows = get_database().checkins.find({"user_id": ObjectId(user_id)}).sort("recorded_on", -1).limit(limit)
    return [serialize_checkin(row) for row in rows]
