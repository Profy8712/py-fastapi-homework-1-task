from pydantic import BaseModel
from typing import List, Optional


class MovieDetailResponseSchema(BaseModel):
    id: int
    name: str
    date: str  # ISO date string (YYYY-MM-DD)
    score: float
    genre: str
    overview: str
    crew: str
    orig_title: str
    status: str
    orig_lang: str
    budget: float
    revenue: float
    country: str

    model_config = {
        "from_attributes": True
    }


class MovieListResponseSchema(BaseModel):
    movies: List[MovieDetailResponseSchema]
    prev_page: Optional[str] = None
    next_page: Optional[str] = None
    total_pages: int
    total_items: int
