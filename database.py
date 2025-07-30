from sqlmodel import SQLModel, create_engine, Session
from contextlib import contextmanager
from typing import Generator

from config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False},
)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


def init_db():
    SQLModel.metadata.create_all(engine)
