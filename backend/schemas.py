from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_bytes(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 UTF-8 bytes")
        return value


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    profile_complete: bool


class AuthOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class HealthProfileIn(BaseModel):
    age: int = Field(ge=13, le=120)
    height_cm: float = Field(ge=100, le=250)
    weight_kg: float = Field(ge=25, le=350)
    smoker: bool = False
    alcohol_per_week: int = Field(default=0, ge=0, le=100)
    activity_goal_minutes: int = Field(default=150, ge=0, le=2000)
    sleep_goal_hours: float = Field(default=8, ge=4, le=12)
    conditions: list[str] = Field(default_factory=list, max_length=20)

    @field_validator("conditions")
    @classmethod
    def clean_conditions(cls, values: list[str]) -> list[str]:
        return list(dict.fromkeys(value.strip()[:80] for value in values if value.strip()))


class HealthProfileOut(HealthProfileIn):
    updated_at: datetime


class CheckInIn(BaseModel):
    recorded_on: date = Field(default_factory=date.today)
    mood: int = Field(ge=1, le=5)
    stress: int = Field(ge=1, le=10)
    sleep_hours: float = Field(ge=0, le=24)
    active_minutes: int = Field(ge=0, le=1440)
    steps: int = Field(default=0, ge=0, le=100000)
    water_liters: float = Field(default=0, ge=0, le=15)
    resting_heart_rate: int | None = Field(default=None, ge=30, le=240)
    note: str = Field(default="", max_length=500)


class CheckInOut(CheckInIn):
    id: str
    created_at: datetime


class SimulationIn(BaseModel):
    sleep_hours: float | None = Field(default=None, ge=0, le=24)
    active_minutes: int | None = Field(default=None, ge=0, le=1440)
    stress: int | None = Field(default=None, ge=1, le=10)
    smoker: bool | None = None
    weight_kg: float | None = Field(default=None, ge=25, le=350)


class CoachIn(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
