import pytest
from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_schema_returns_text():
    response = client.get("/schema")
    assert response.status_code == 200
    assert "schema" in response.json()


def test_execute_blocks_drop():
    response = client.post("/execute", json={"sql": "DROP TABLE customers"})
    assert response.status_code == 400
    assert "Blocked" in response.json()["detail"]


def test_execute_blocks_delete():
    response = client.post("/execute", json={"sql": "DELETE FROM orders"})
    assert response.status_code == 400


def test_execute_blocks_non_select():
    response = client.post("/execute", json={"sql": "INSERT INTO customers VALUES ('X','Y')"})
    assert response.status_code == 400


def test_execute_valid_select():
    response = client.post("/execute", json={"sql": "SELECT 1 AS num"})
    assert response.status_code == 200
    data = response.json()
    assert "columns" in data
    assert "rows" in data


def test_query_empty_question():
    response = client.post("/query", json={"question": ""})
    assert response.status_code == 400
