"""
Customer schemas
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class CustomerBase(BaseModel):
    customer_id: int
    customer_name: str
    descriptive_name: Optional[str] = None
    currency_code: str = 'INR'
    time_zone: str = 'Asia/Kolkata'
    status: str = 'ENABLED'


class CustomerResponse(CustomerBase):
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CustomerListResponse(BaseModel):
    customers: list[CustomerResponse]
    total: int
