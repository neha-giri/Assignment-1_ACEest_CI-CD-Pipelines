import pytest
from app import app, clients, calculate_calories


@pytest.fixture
def client():
    app.config["TESTING"] = True
    clients.clear()
    with app.test_client() as c:
        yield c


def test_home(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.get_json()["status"] == "running"


def test_health(client):
    assert client.get("/health").get_json() == {"status": "healthy"}


def test_list_programs(client):
    data = client.get("/programs").get_json()
    assert set(data) == {"FL", "MG", "BG"}


def test_get_program(client):
    r = client.get("/programs/fl")
    assert r.status_code == 200
    assert r.get_json()["calorie_factor"] == 22


def test_get_program_not_found(client):
    assert client.get("/programs/XX").status_code == 404


@pytest.mark.parametrize("weight,prog,expected",
                         [(70, "FL", 1540), (70, "MG", 2450), (70, "BG", 1820)])
def test_calculate_calories(weight, prog, expected):
    assert calculate_calories(weight, prog) == expected


def test_calculate_calories_invalid():
    with pytest.raises(ValueError):
        calculate_calories(-5, "FL")
    with pytest.raises(ValueError):
        calculate_calories(70, "ZZ")


def test_calories_endpoint(client):
    r = client.post("/calories", json={"weight": 80, "program": "MG"})
    assert r.get_json()["calories"] == 2800


def test_calories_endpoint_bad_input(client):
    assert client.post("/calories", json={"weight": "abc"}).status_code == 400


def test_add_and_get_client(client):
    payload = {"name": "Arun", "age": 25, "weight": 70, "program": "FL", "adherence": 80}
    r = client.post("/clients", json=payload)
    assert r.status_code == 201
    assert r.get_json()["calories"] == 1540
    assert client.get("/clients/Arun").get_json()["program"] == "FL"
    assert len(client.get("/clients").get_json()) == 1


def test_add_client_validation(client):
    assert client.post("/clients", json={"name": "", "program": "FL"}).status_code == 400
    bad = {"name": "X", "program": "FL", "adherence": 150}
    assert client.post("/clients", json=bad).status_code == 400
    bad = {"name": "X", "program": "FL", "age": "old"}
    assert client.post("/clients", json=bad).status_code == 400


def test_duplicate_client(client):
    payload = {"name": "Arun", "program": "BG", "weight": 60}
    client.post("/clients", json=payload)
    assert client.post("/clients", json=payload).status_code == 409


def test_delete_client(client):
    client.post("/clients", json={"name": "Arun", "program": "BG", "weight": 60})
    assert client.delete("/clients/Arun").status_code == 200
    assert client.delete("/clients/Arun").status_code == 404
    assert client.get("/clients/Arun").status_code == 404
