from sqlalchemy import Column, Integer, Text, Boolean, Float, DateTime, String
from db_models.user import Base


class MovieDBModel(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    price = Column(Integer)
    description = Column(Text)
    image_url = Column(Text, nullable=True)
    location = Column(String)
    published = Column(Boolean)
    rating = Column(Float)
    genre_id = Column(Integer)
    created_at = Column(DateTime)