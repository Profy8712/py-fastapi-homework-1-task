from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from decimal import Decimal


from database import get_db, MovieModel
from schemas.movies import MovieListResponseSchema, MovieDetailResponseSchema

router = APIRouter()

def model_to_dict(movie: MovieModel) -> dict:
    return {
        "id": movie.id,
        "name": movie.name,
        "date": str(movie.date),  # приводим к строке!
        "score": movie.score,
        "genre": movie.genre,
        "overview": movie.overview,
        "crew": movie.crew,
        "orig_title": movie.orig_title,
        "status": movie.status,
        "orig_lang": movie.orig_lang,
        "budget": float(movie.budget) if isinstance(movie.budget, Decimal) else movie.budget,
        "revenue": float(movie.revenue),
        "country": movie.country,
    }

@router.get("/movies/", response_model=MovieListResponseSchema)
async def get_movies(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number (>=1)"),
    per_page: int = Query(10, ge=1, le=20, description="Movies per page (1-20)")
):
    total_items_result = await db.execute(select(func.count()).select_from(MovieModel))
    total_items = total_items_result.scalar_one()
    if total_items == 0:
        raise HTTPException(status_code=404, detail="No movies found.")

    total_pages = (total_items + per_page - 1) // per_page
    if page > total_pages:
        raise HTTPException(status_code=404, detail="No movies found.")

    offset = (page - 1) * per_page

    movies_result = await db.execute(
        select(MovieModel).order_by(MovieModel.id.asc()).offset(offset).limit(per_page)
    )
    movies = movies_result.scalars().all()
    if not movies:
        raise HTTPException(status_code=404, detail="No movies found.")

    prefix = "/api/v1/theater/movies/"
    prev_page = (
        f"{prefix}?page={page - 1}&per_page={per_page}" if page > 1 else None
    )
    next_page = (
        f"{prefix}?page={page + 1}&per_page={per_page}" if page < total_pages else None
    )

    return MovieListResponseSchema(
        movies=[MovieDetailResponseSchema(**model_to_dict(m)) for m in movies],
        prev_page=prev_page,
        next_page=next_page,
        total_pages=total_pages,
        total_items=total_items,
    )

@router.get("/movies/{movie_id}/", response_model=MovieDetailResponseSchema)
async def get_movie_by_id(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
):
    movie = await db.get(MovieModel, movie_id)
    if not movie:
        raise HTTPException(
            status_code=404, detail="Movie with the given ID was not found."
        )
    return MovieDetailResponseSchema(**model_to_dict(movie))
