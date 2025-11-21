import pytest
import os
import sys

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test the health endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'ok'

def test_loans_endpoint_structure(client):
    """Test the loans endpoint returns proper structure"""
    response = client.get('/api/loans')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_stats_endpoint_structure(client):
    """Test the stats endpoint returns proper structure"""
    response = client.get('/api/stats')
    assert response.status_code == 200
    data = response.json
    assert 'total_loans' in data
    assert 'total_amount' in data
    assert 'avg_amount' in data