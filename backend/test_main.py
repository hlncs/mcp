"""
Unit tests for FastAPI application
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self):
        """Test GET /health returns healthy status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "python_version" in data
        assert data["message"] == "API is running"


class TestRootEndpoint:
    """Test root endpoint"""
    
    def test_root(self):
        """Test GET / returns welcome message"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Welcome to MCP API"


class TestPlanEndpoints:
    """Test planning endpoints"""
    
    def test_create_plan(self):
        """Test creating a new plan"""
        payload = {"query": "What is AI?", "context": {"source": "test"}}
        response = client.post("/plan", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "plan_id" in data
        assert data["status"] == "processing"
        assert data["query"] == "What is AI?"
    
    def test_create_plan_alias_endpoint(self):
        """Test creating plan via /plan/create alias"""
        payload = {"query": "Test via alias", "context": {}}
        response = client.post("/plan/create", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processing"
    
    def test_get_plan(self):
        """Test retrieving plan status"""
        create_response = client.post("/plan", json={"query": "Test"})
        plan_id = create_response.json()["plan_id"]
        response = client.get(f"/plan/{plan_id}")
        assert response.status_code == 200
        assert response.json()["plan_id"] == plan_id
    
    def test_get_plan_not_found(self):
        """Test getting non-existent plan returns 404"""
        response = client.get("/plan/nonexistent-id")
        assert response.status_code == 404
    
    def test_list_plans(self):
        """Test listing all plans"""
        response = client.get("/plans")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "plans" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
