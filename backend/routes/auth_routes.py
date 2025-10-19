from fastapi import APIRouter, HTTPException
from models.auth_model import RegisterIn, LoginIn
from pymongo import MongoClient
from datetime import datetime, timedelta
import os, bcrypt, jwt
from utils.auth_utils import get_current_user

router = APIRouter()

MONGO_URI = os.getenv('MONGODB_URI') or os.getenv('MONGO_URI') or 'mongodb://localhost:27017'
client = MongoClient(MONGO_URI)
db = client['vitatwin']
users = db['auth_users']

JWT_SECRET = os.getenv('JWT_SECRET', 'change_me')
JWT_ALG = 'HS256'

@router.post('/register')
async def register(payload: RegisterIn):
    if users.find_one({'email': payload.email}):
        raise HTTPException(status_code=400, detail='User already exists')
    hashed = bcrypt.hashpw(payload.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    users.insert_one({'email': payload.email, 'password': hashed, 'name': payload.name, 'created_at': datetime.utcnow()})
    return {'ok': True, 'email': payload.email}

@router.post('/login')
async def login(payload: LoginIn):
    user = users.find_one({'email': payload.email})
    if not user or not bcrypt.checkpw(payload.password.encode('utf-8'), user['password'].encode('utf-8')):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    token = jwt.encode({'sub': str(user['_id']), 'exp': datetime.utcnow() + timedelta(days=7)}, JWT_SECRET, algorithm=JWT_ALG)
    return {'access_token': token, 'token_type': 'bearer'}

@router.get('/me')
async def me(user_id: str = get_current_user):
    return {'user_id': user_id, 'message': 'Authenticated'}
