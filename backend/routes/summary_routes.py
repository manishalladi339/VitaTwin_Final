from fastapi import APIRouter, HTTPException, Depends
from models.summary_model import SummaryIn
import openai, os
from utils.auth_utils import get_current_user

router = APIRouter()
openai.api_key = os.getenv('OPENAI_API_KEY')

@router.post('/')
async def summarize(payload: SummaryIn, user_id: str = Depends(get_current_user)):
    if not openai.api_key:
        raise HTTPException(status_code=500, detail='OPENAI_API_KEY not set')
    prompt = f"Summarize the following text into a concise, friendly paragraph focusing on health-related insights and next steps:\n\n{payload.text}"
    try:
        resp = openai.ChatCompletion.create(
            model='gpt-4-turbo',
            messages=[{'role': 'system', 'content': 'You are a concise health summarizer.'},
                      {'role': 'user', 'content': prompt}],
            temperature=0.4,
            max_tokens=200
        )
        content = resp['choices'][0]['message']['content']
        return {'summary': content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
