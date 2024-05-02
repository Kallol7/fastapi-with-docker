import psycopg
from psycopg.rows import dict_row
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time

with open("secrets/postgres_pass.txt","r") as f:
            postgres_pass = f.read()
engine = create_engine(f"postgresql+psycopg://postgres:{postgres_pass}@localhost/fastapi")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def connect_database():
    while True:
        try:
            # uvicorn app.main:app --reload
            with open("secrets/dbconfig.txt","r") as f:
                dbconfig = f.read()
            connection = psycopg.connect(dbconfig, row_factory=dict_row)
            dbconfig = "" # configuration info removed
            print("Database connected.")
            break
        except Exception as e:
            print("Database connection failed,", e)
            time.sleep(2)

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
