# test/conftest.py
import pytest
from sqlmodel import create_engine, SQLModel


@pytest.fixture()
def test_engine():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture()
def patch_engine(monkeypatch, test_engine):
    monkeypatch.setattr("database.engine", test_engine)
