from fastapi import FastAPI
from models.database_orm import engine, Base
from handlers import posts_handler, users_handler


Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def home():
    return "Home"


app.include_router(posts_handler.router)
app.include_router(users_handler.router)
