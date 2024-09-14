from fastapi import FastAPI
from models.database_orm import engine, Base
from handlers import posts_handler, users_handler, comments_handler
from models.auth_model import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from utilities.settings import setting

Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return "Home"


app.include_router(posts_handler.router)
app.include_router(users_handler.router)
app.include_router(comments_handler.router)
app.include_router(auth_router)

# if __name__ == "__main__":
#     uvicorn.run("app:app", host=setting.host, port=setting.port)
