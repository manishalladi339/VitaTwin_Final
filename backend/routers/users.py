from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from core.database import get_database
from core.security import current_user_id
from schemas import HealthProfileIn, HealthProfileOut

router = APIRouter()


@router.get("", response_model=HealthProfileOut)
def get_profile(user_id: str = Depends(current_user_id)):
    user = get_database().users.find_one({"_id": ObjectId(user_id)}, {"health_profile": 1})
    if not user or not user.get("health_profile"):
        raise HTTPException(status_code=404, detail="Complete your health profile first")
    return user["health_profile"]


@router.put("", response_model=HealthProfileOut)
def put_profile(payload: HealthProfileIn, user_id: str = Depends(current_user_id)):
    profile = {**payload.model_dump(), "updated_at": datetime.now(timezone.utc)}
    result = get_database().users.update_one({"_id": ObjectId(user_id)}, {"$set": {"health_profile": profile}})
    if not result.matched_count:
        raise HTTPException(status_code=404, detail="Account not found")
    return profile
