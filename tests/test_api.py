from mypackage.crud import get_user_by_email


def test_read_main(test_client):
    response = test_client.get("/api")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {"Hello": "World"}


def test_get_items(test_client):
    response = test_client.get("/api/items/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == []


def test_get_users(test_client):
    response = test_client.get("/api/users")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == []


def test_post_user(test_client, test_db):
    test_user = {"email": "test@example.com", "password": "testpassword"}

    response = test_client.post("/api/users/", json=test_user)

    assert response.status_code == 201
    content = response.json()

    assert "email" in content
    assert content["email"] == "test@example.com"
    assert "password" not in content
    assert "id" in content
    assert type(content["id"]) is int
    assert content["is_active"]

    user = get_user_by_email(test_db, email=test_user["email"])
    assert user.email == test_user["email"]

    # Duplicate User
    response = test_client.post("/api/users/", json=test_user)
    assert response.status_code == 422
    assert response.json()["detail"] == "Email 'test@example.com' already registered"


def test_get_users_after_post(test_client):
    response = test_client.get("/api/users")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    content = response.json()
    assert len(content) == 1
    for user in content:
        assert "email" in user
        assert "password" not in user
        assert "id" in user
        assert "is_active" in user


def test_create_item(test_client):
    item = {"title": "test name", "description": "test description"}
    response = test_client.post("/api/items/", json=item)
    assert response.status_code == 201
    assert response.json() == item


def test_create_item_for_user(test_client):
    response = test_client.get("/api/users")
    content = response.json()
    assert len(content) == 1
    user = content[0]
    expected_email = "test@example.com"
    assert user["email"] == expected_email
    user_id = user["id"]

    item = {"title": "Item2"}
    response = test_client.post(f"/api/users/{user_id}/items/", json=item)
    assert response.status_code == 201

    item_response_content = response.json()
    assert item_response_content["owner_id"] == user_id

    response = test_client.post(f"/api/users/{user_id + 1}/items/", json=item)
    assert response.status_code == 404
    assert response.json()["detail"] == "User with id '2' not found"
