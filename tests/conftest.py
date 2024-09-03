from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app import models
from app.main import app
from app.config import settings
from app.database import get_db, Base
from alembic import command
from app.oauth2 import create_access_token

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

client = TestClient(app)


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    # command.upgrade("head")
    # command.upgrade("base")
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def test_user(client):
    user_data = {"email": "rishav@gmail.com", "password": "pass123"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def test_user2(client):
    user_data = {"email": "rishu@gmail.com", "password": "pass123"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user["id"]})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
    return client


@pytest.fixture
def test_posts(test_user, session, test_user2):
    posts_data = [
        {
            "title": "1st Title",
            "content": "1st Content",
            "owner_id": test_user["id"],
        },
        {
            "title": "2nd Title",
            "content": "2nd Content",
            "owner_id": test_user["id"],
        },
        {
            "title": "3rd Title",
            "content": "3rd Content",
            "owner_id": test_user["id"],
        },
        {
            "title": "4th Title",
            "content": "4th Content",
            "owner_id": test_user2["id"],
        },
    ]
    post_map = list(map(lambda post: models.Post(**post), posts_data))
    # post_list = [models.Post(**i) for i in posts_data]
    session.add_all(post_map)
    session.commit()

    posts = session.query(models.Post).order_by(models.Post.id).all()
    return posts
