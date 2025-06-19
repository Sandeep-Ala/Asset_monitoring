# models/filters.py

from typing import Optional, List
from pydantic import BaseModel

class QueryFilters(BaseModel):
    year: Optional[int]
    month: Optional[int]
    equipment: Optional[str]
    day: Optional[int]
    dcu: Optional[int]
    start_time: Optional[str]  # Example: '2025-02-02T00:00:00Z'
    end_time: Optional[str]    # Example: '2025-02-02T23:59:59Z'
    metrics: Optional[List[str]]
    window_period: Optional[str]  # Example: '1 hour', '30 minutes', etc.
    where_args:Optional[List[str]]