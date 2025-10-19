from fastapi import APIRouter, Depends
from utils.auth_utils import get_current_user
from pymongo import MongoClient
import os

router = APIRouter()

MONGO_URI = os.getenv('MONGODB_URI') or os.getenv('MONGO_URI') or 'mongodb://localhost:27017'
client = MongoClient(MONGO_URI)
db = client['vitatwin']

@router.get('/profile')
async def profile(user_id: str = Depends(get_current_user)):
    return {"user_id": user_id, "message": "Authenticated"}
