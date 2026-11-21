from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_serializer
from app.models.order import OrderStatus

class OrderBase(BaseModel):
    total_amount: Decimal = Field(
        ...,
        gt=0,
        max_digits = 10,
        decimal_places = 2,     
        description="El monto total debe de ser mayor a 0"
    )


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    status: OrderStatus | None = Field(default= None)
    total_amount: Decimal | None = Field(
        default=None, gt=0,  max_digits= 10, decimal_places=2
    )


class OrderResponse(OrderBase):
    id: int
    order_code: str
    status: OrderStatus 
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("total_amount")
    def serialize_total_amount(self, value:Decimal) -> float:
        return float(value)