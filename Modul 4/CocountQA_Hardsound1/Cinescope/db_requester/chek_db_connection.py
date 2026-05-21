from sqlalchemy import text
from db_requester.db_client import engine

with engine.connect() as connection:
    result = connection.execute(text("SELECT 1"))
    print(result.scalar())