import pytest

from aceest import create_app


@pytest.fixture
def client(tmp_path):
    # every test gets its own throwaway sqlite file so tests don't affect each other
    app = create_app({"DATABASE": str(tmp_path / "test.db"), "TESTING": True})
    return app.test_client()


@pytest.fixture
def sample_client():
    return {
        "name": "Asha Rao",
        "age": 28,
        "height": 165,
        "weight": 70,
        "program": "FL",
        "target_weight": 62,
        "target_adherence": 90,
        "membership_end": "2099-12-31",
    }


@pytest.fixture
def saved_client(client, sample_client):
    # a client that already exists in the db, used by the sub-resource tests
    client.post("/clients", json=sample_client)
    return sample_client["name"]
