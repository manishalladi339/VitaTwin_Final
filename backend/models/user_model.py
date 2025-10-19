from pydantic import BaseModel
from typing import Optional
class UserHealth(BaseModel):
    name: str
    age: int
    weight: float
    height: float
    smoker: bool
    drinker: bool
    mood: Optional[str] = None
    stress_level: Optional[str] = None
    sleep_hours: Optional[float] = None
    activity_level: Optional[str] = None
    diet_quality: Optional[str] = None
