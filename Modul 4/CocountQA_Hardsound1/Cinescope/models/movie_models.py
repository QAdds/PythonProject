from typing import List, Optional
from pydantic import BaseModel


class GenreResponse(BaseModel):
    name: str


class MovieItemResponse(BaseModel):
    id: int                      # int, не str
    name: str
    description: str
    genreId: int
    imageUrl: Optional[str]      # может быть null
    price: int
    rating: int
    location: str
    published: bool
    createdAt: str               # можно потом сделать datetime, но пока хватит str
    genre: GenreResponse         # вложенный объект


class MoviesListResponse(BaseModel):
    movies: List[MovieItemResponse]
    count: int
    page: int
    pageSize: int
    pageCount: int
