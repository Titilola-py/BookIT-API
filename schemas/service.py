from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone


class ServiceBase(BaseModel):
    title: str = Field(..., example="Babysitting")
    description: Optional[str] = Field(
        None, example="Professional babysitting service for children of all ages"
    )
    price: float = Field(..., example=50.00)
    duration_minutes: int = Field(..., example=180)  # 3 hours


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    title: Optional[str] = Field(None, example="Babysitting")
    description: Optional[str] = Field(
        None, example="Professional babysitting service for children of all ages"
    )
    price: Optional[float] = Field(None, example=50.00)
    duration_minutes: Optional[int] = Field(None, example=180)


class ServiceResponse(ServiceBase):
    id: UUID
    is_active: bool
    created_at: datetime
    owner_id: UUID

    class Config:
        from_attributes = True
