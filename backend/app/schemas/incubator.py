from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class IncubatorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # Інформація про інкубатор
    id: int
    device_code: str
    company_id: int
    number: int

    device_type: str
    capacity: int | None

    eggs_amount: int | None
    activated_at: datetime | None
    state: str
    instruction_id: int | None
    instruction_title: str | None = None

    # Поточні рекомендовані параметри
    parameters: dict = Field(default_factory=dict)

    # Прогрес інкубації
    duration_days: int | None = None
    current_day: int | None = None
    days_remaining: int | None = None
    estimated_end_at: datetime | None = None
    progress: float | None = None