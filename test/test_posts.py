import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.posts import PostSchemaAdd, PostResponse, PostLiteResponse
from app.services.posts import PostService
from unittest.mock import AsyncMock, patch

# Initialize a TestClient
client = TestClient(app)

@pytest.fixture
def mock_post_service():
    """Fixture to mock PostService."""
    with patch('app.services.posts.PostService', autospec=True) as mock:
        yield mock

@pytest.fixture
def admin_user():
    """Fixture for a mock admin user."""
    return {"id": 1, "username": "admin", "is_admin": True}

@pytest.mark.asyncio
async def test_get_posts(mock_post_service, admin_user):
    mock_post_service.return_value.get_posts.return_value = [
        PostLiteResponse(id=1, title="Post 1", content="Content 1"),
        PostLiteResponse(id=2, title="Post 2", content="Content 2"),
    ]
    
    response = client.get("/posts/", headers={"Authorization": "Bearer fake_token"})
    
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["title"] == "Post 1"

@pytest.mark.asyncio
async def test_get_post(mock_post_service, admin_user):
    mock_post_service.return_value.get_post_by_id.return_value = PostResponse(
        id=1, title="Post 1", content="Content 1"
    )

    response = client.get("/posts/1", headers={"Authorization": "Bearer fake_token"})
    
    assert response.status_code == 200
    assert response.json()["title"] == "Post 1"

@pytest.mark.asyncio
async def test_add_post(mock_post_service, admin_user):
    post_data = PostSchemaAdd(title="New Post", content="New Content")
    mock_post_service.return_value.add_post.return_value = 1

    response = client.post(
        "/posts/", json=post_data.dict(), headers={"Authorization": "Bearer fake_token"}
    )
    
    assert response.status_code == 201
    assert response.json()["title"] == "New Post"

@pytest.mark.asyncio
async def test_update_post(mock_post_service, admin_user):
    post_data = PostSchemaAdd(title="Updated Post", content="Updated Content")
    mock_post_service.return_value.update_post.return_value = PostResponse(
        id=1, title="Updated Post", content="Updated Content"
    )

    response = client.put(
        "/posts/1", json=post_data.dict(), headers={"Authorization": "Bearer fake_token"}
    )
    
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Post"

@pytest.mark.asyncio
async def test_delete_post(mock_post_service, admin_user):
    response = client.delete("/posts/1", headers={"Authorization": "Bearer fake_token"})
    
    assert response.status_code == 204
    mock_post_service.return_value.delete_post.assert_called_once_with(1)


