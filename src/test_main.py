import pytest
from fastapi.testclient import TestClient
from main import app
from models.books import Roll
from datetime import datetime


@pytest.fixture
def mock_storage(mocker):
    mock = mocker.Mock()
    return mock


@pytest.fixture
def client(mock_storage):
    def get_mock_storage():
        return mock_storage

    app.dependency_overrides = get_mock_storage
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_create_roll(client, mock_storage):
    mock_storage.create_roll.return_value = Roll(
        id=1,
        length=10.5,
        weight=200.0,
        added_date=datetime.utcnow(),
        removed_date=None,
    )

    response = client.post('/rolls/', json={'length': 10.5, 'weight': 200.0})
    assert response.status_code == 200
    assert response.json()['length'] == 10.5
    assert response.json()['weight'] == 200.0


def test_delete_roll(client, mock_storage):
    mock_storage.delete_roll.return_value = Roll(
        id=1,
        length=10.5,
        weight=200.0,
        added_date=datetime.utcnow(),
        removed_date=datetime.utcnow(),
    )

    response = client.delete('/rolls/1')
    assert response.status_code == 200
    assert response.json()['id'] == 1


def test_get_rolls(client, mock_storage):
    mock_storage.get_rolls.return_value = [
        Roll(id=1, length=10.5, weight=200.0, added_date=datetime.utcnow(), removed_date=None),
        Roll(id=2, length=15.0, weight=300.0, added_date=datetime.utcnow(), removed_date=None),
    ]

    response = client.get('/rolls/')
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_stats(client, mock_storage):
    mock_storage.get_stats.return_value = {
        'added_count': 2,
        'removed_count': 1,
        'avg_length': 12.75,
        'avg_weight': 250.0,
        'max_length': 15.0,
        'min_length': 10.5,
        'max_weight': 300.0,
        'min_weight': 200.0,
        'total_weight': 500.0,
        'max_duration': 10,
        'min_duration': 5,
        'min_count_day': '2023-01-01',
        'max_count_day': '2023-01-02',
        'min_weight_day': '2023-01-01',
        'max_weight_day': '2023-01-02',
    }

    response = client.get('/rolls/stats/', params={'start_date': '2023-01-01', 'end_date': '2023-01-31'})
    assert response.status_code == 200
    assert response.json()['added_count'] == 2
    assert response.json()['total_weight'] == 500.0
