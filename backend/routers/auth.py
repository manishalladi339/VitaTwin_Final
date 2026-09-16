from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from pymongo.errors import DuplicateKeyError

from core.database import get_database
from core.security import create_token, current_user_id, hash_password, verify_password
from schemas import AuthOut, LoginIn, RegisterIn, UserOut

router = APIRouter()


def public_user(user: dict) -> UserOut:
    return UserOut(id=str(user["_id"]), name=user["name"], email=user["email"], profile_complete=bool(user.get("health_profile")))


@router.post("/register", response_model=AuthOut, status_code=201)
def register(payload: RegisterIn):
    document = {
        "name": payload.name.strip(),
        "email": payload.email.lower(),
        "password_hash": hash_password(payload.password),
        "created_at": datetime.now(timezone.utc),
    }
    try:
        result = get_database().users.insert_one(document)
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=409, detail="An account with this email already exists") from exc
    document["_id"] = result.inserted_id
    return AuthOut(access_token=create_token(str(result.inserted_id)), user=public_user(document))


@router.post("/login", response_model=AuthOut)
def login(payload: LoginIn):
    user = get_database().users.find_one({"email": payload.email.lower()})
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return AuthOut(access_token=create_token(str(user["_id"])), user=public_user(user))


@router.get("/me", response_model=UserOut)
def me(user_id: str = Depends(current_user_id)):
    try:
        user = get_database().users.find_one({"_id": ObjectId(user_id)})
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid token subject") from exc
    if not user:
        raise HTTPException(status_code=401, detail="Account no longer exists")
    return public_user(user)
