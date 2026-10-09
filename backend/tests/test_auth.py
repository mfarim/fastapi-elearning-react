import pytest
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token


def test_password_hashing():
    pwd = "secretpassword"
    hashed = get_password_hash(pwd)
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_jwt_token_creation_and_decoding():
    token = create_access_token(subject=1, roles=["ROLE_ADMIN"], extra_claims={"name": "Admin"})
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "1"
    assert "ROLE_ADMIN" in payload["roles"]
    assert payload["name"] == "Admin"


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "database" in data
    assert "redis" in data
