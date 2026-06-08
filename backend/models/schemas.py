from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime


class Asset(BaseModel):
    symbol: str
    name: str
    asset_type: Literal["stock", "crypto", "forex"]
    price: Optional[float] = None
    change_percent: Optional[float] = None


class OrderRequest(BaseModel):
    asset_symbol: str
    asset_type: Literal["stock", "crypto", "forex"]
    quantity: float = Field(gt=0)


class OrderResponse(BaseModel):
    id: int
    user_id: int
    asset_symbol: str
    asset_type: str
    transaction_type: Literal["buy", "sell"]
    quantity: float
    price: float
    total_amount: float
    timestamp: datetime


class PortfolioItem(BaseModel):
    asset_symbol: str
    asset_type: str
    total_quantity: float
    avg_cost_basis: float
    current_price: Optional[float] = None
    unrealized_pnl: Optional[float] = None


class PerformanceMetrics(BaseModel):
    total_invested: float
    current_value: float
    total_return: float
    total_return_percent: float


class ScenarioRequest(BaseModel):
    name: str
    asset_symbol: str
    asset_type: Literal["stock", "crypto", "forex"]
    hypothetical_date: str  # ISO format YYYY-MM-DD
    hypothetical_amount: float = Field(gt=0)


class ScenarioResult(BaseModel):
    scenario_id: int
    name: str
    asset_symbol: str
    hypothetical_date: str
    hypothetical_amount: float
    current_price: Optional[float] = None
    hypothetical_value: Optional[float] = None
    gain_loss: Optional[float] = None
    gain_loss_percent: Optional[float] = None
