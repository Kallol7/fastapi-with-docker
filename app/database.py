# import psycopg
# from psycopg.rows import dict_row
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# import time
from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy_utils import database_exists, create_database
from . import models
from .config import postgres_user, postgres_pass, host, dbname

engine = create_async_engine(f"postgresql+psycopg://{postgres_user}:{postgres_pass}@{host}/{dbname}")

SessionLocal  = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not database_exists(engine.url):
        create_database(engine.url)

    async with engine.begin() as connection:
         await connection.run_sync(models.Base.metadata.create_all)
    # everything before yield will run once before taking requests
    yield

# Dependency
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()

# def connect_database():
#     while True:
#         try:
#             # uvicorn app.main:app --reload
#             connection = psycopg.connect(config.psycopg_config, row_factory=dict_row)
#             print("Database connected.")
#             break
#         except Exception as e:
#             print("Database connection failed,", e)
#             time.sleep(2)

## WITHOUT ORM ##
# @app.get("/posts")
# async def get_posts():
#     with connection.cursor() as cursor:
#         rows = "id, title, content, published"
#         cursor.execute(f"SELECT {rows} FROM posts")
#         return {"data": cursor.fetchall()}
# 
# @app.get("/posts/{id:int}")
# async def get_post(id: int):
#     with connection.cursor() as cursor:
#         rows = "id, title, content, published"
#         cursor.execute(f"SELECT {rows} FROM posts where id=%s", params=[id])
#         post = cursor.fetchone()
#         if post:
#             return post
#         else:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The post with id: {id} was not found")
# 
# @app.post("/posts", status_code=status.HTTP_201_CREATED)
# async def create_posts(post: schemas.Post):
#     with connection.cursor() as cursor:
#         cursor.execute("""
#             INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) 
#             RETURNING id,title,content,published
#         """, [post.title,post.content,post.published])
#         new_post = cursor.fetchone()
#         if new_post:
#             connection.commit()
#             return {
#                 "message": "Post has been created",
#                 "data": new_post
#             }
#         else:
#             connection.rollback()
#             return {
#                 "message": "Something went wrong",
#                 "data": None
#             }
# 
# @app.put("/posts/{id}")
# async def update_post(id: int, post: schemas.Post):
#     with connection.cursor() as cursor:
#         cursor.execute("""
#             UPDATE posts SET title=%s, content=%s, published=%s WHERE id=%s 
#             RETURNING  id,title,content,published
#         """, [post.title,post.content,post.published, id])
#         updated = cursor.fetchone()
#         if updated:
#             connection.commit()
#             return {
#                 "message": "Post has been updated",
#                 "data": updated
#             }
#         else:
#             connection.rollback()
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The post with id: {id} was not found")
# 
# @app.delete("/posts/{id:int}")
# async def delete_post(id: int):
#     with connection.cursor() as cursor:
#         cursor.execute("DELETE FROM posts where id=%s", params=[id])
#         if cursor.rowcount==1:
#             print("Deleted")
#             connection.commit()
#             return Response(status_code=status.HTTP_204_NO_CONTENT)
#         else:
#             connection.rollback()
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The post with id: {id} was not found")
