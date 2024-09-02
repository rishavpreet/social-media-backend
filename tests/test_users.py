import pytest
from app.config import settings
from app import schemas
from jose import jwt


# @app.get("/")
# def test_root(client):
#     res = client.get("/")
#     print(res.json())
#     assert res.json().get("message") == "This is a social media backend"
#     assert res.status_code == 200


def test_create_user(client):
    res = client.post(
        "/users/", json={"email": "rishav@gmail.com", "password": "pass123"}
    )
    new_user = schemas.UserOut(**res.json())
    assert new_user.email == "rishav@gmail.com"
    assert res.status_code == 201


def test_login_user(client, test_user):
    res = client.post(
        "/login",
        data={"username": test_user["email"], "password": test_user["password"]},
    )
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(
        login_res.access_token, settings.secret_key, algorithms=[settings.algorithm]
    )
    id_ = payload.get("user_id")
    assert id_ == test_user["id"]
    assert login_res.token_type == "bearers"
    assert res.status_code == 200


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("wrongemail@gmail.com", "pass123", 403),
        ("rishav@gmail.com", "wrongpass", 403),
        ("wrongemail@gmail.com", "wrongpass", 403),
        (None, "pass123", 422),
        ("rishav@gmail.com", None, 422),
    ],
)
def test_incorrect_login(email, password, status_code, test_user, client):
    res = client.post(
        "/login",
        data={"username": email, "password": password},
    )
    assert res.status_code == status_code
