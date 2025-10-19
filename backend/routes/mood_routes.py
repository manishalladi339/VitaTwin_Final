from fastapi import APIRouter, HTTPException, Depends
from models.mood_model import MoodIn
import openai, os, json, re
from utils.auth_utils import get_current_user

router = APIRouter()
openai.api_key = os.getenv('OPENAI_API_KEY')

def _safe_parse_json(text: str):
    try:
        return json.loads(text)
    except Exception:
        pass
    m = re.search(r'\{[\s\S]*\}', text)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    return {"mood": "Neutral", "confidence": 0.5, "reasoning": "Fallback; model returned non-JSON."}

@router.post('/analyze')
async def analyze(payload: MoodIn, user_id: str = Depends(get_current_user)):
    if not openai.api_key:
        raise HTTPException(status_code=500, detail='OPENAI_API_KEY not set')
    prompt = (
        "Classify the mood of this text as Positive, Neutral, or Negative. "
        "Also provide a confidence score 0-1 and one-sentence reasoning. "
        "Return ONLY compact JSON with keys: mood, confidence, reasoning.\n\n"
        f"Text: {payload.text}"
    )
    try:
        resp = openai.ChatCompletion.create(
            model='gpt-4-turbo',
            messages=[{'role': 'system', 'content': 'You are a precise mood classifier.'},
                      {'role': 'user', 'content': prompt}],
            temperature=0.2,
            max_tokens=180
        )
        content = resp['choices'][0]['message']['content']
        return _safe_parse_json(content.strip())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
