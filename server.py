from fastapi import FastAPI
from database import init_db
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from api.chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
origins = [
    "http://localhost:5173",
    # 也可以用 "*" 允许所有源，但不建议生产环境这么做
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)