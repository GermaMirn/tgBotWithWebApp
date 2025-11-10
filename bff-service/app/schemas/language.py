from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class StudioLanguageBase(BaseModel):
    name: str = Field(..., description="Название языка", example="Английский")
    code: str = Field(..., description="Код языка", example="en")
    is_active: Optional[bool] = Field(default=True, description="Активен ли язык")

class StudioLanguageCreate(StudioLanguageBase):
    pass

class StudioLanguageUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Название языка")
    code: Optional[str] = Field(None, description="Код языка")
    is_active: Optional[bool] = Field(None, description="Активен ли язык")

class StudioLanguageRead(StudioLanguageBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

