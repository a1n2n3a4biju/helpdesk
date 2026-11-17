def make_ticket(client, requester_id, **changes):
    body = {
        "requester_id": requester_id,
        "title": "Keyboard not working",
        "description": "The wireless keyboard stopped typing this morning.",
        "category": "Hardware",
    }
    body.update(changes)
    return client.post("/tickets", json=body)


def test_create_ticket(client, requester):
    response = make_ticket(client, requester.id)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "New"
    assert data["priority"] == "Medium"
    history = client.get(f"/tickets/{data['id']}/history").json()
    assert [row["action"] for row in history] == ["created"]


def test_create_ticket_missing_title(client, requester):
    body = {"requester_id": requester.id, "description": "No title was given for this one."}
    response = client.post("/tickets", json=body)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "title"]


def test_create_ticket_unknown_requester(client):
    response = make_ticket(client, 999999)
    assert response.status_code == 422


def test_get_missing_ticket_returns_404(client):
    response = client.get("/tickets/999999")
    assert response.status_code == 404


def test_valid_status_change(client, requester):
    ticket_id = make_ticket(client, requester.id).json()["id"]
    response = client.patch(f"/tickets/{ticket_id}/status", json={"status": "In Progress"})
    assert response.status_code == 200
    assert response.json()["status"] == "In Progress"
    history = client.get(f"/tickets/{ticket_id}/history").json()
    assert history[-1]["old_status"] == "New"
    assert history[-1]["new_status"] == "In Progress"


def test_invalid_status_change_returns_409(client, requester):
    ticket_id = make_ticket(client, requester.id).json()["id"]
    response = client.patch(f"/tickets/{ticket_id}/status", json={"status": "Resolved"})
    assert response.status_code == 409
    assert client.get(f"/tickets/{ticket_id}").json()["status"] == "New"


def test_patch_cannot_change_status(client, requester):
    ticket_id = make_ticket(client, requester.id).json()["id"]
    response = client.patch(f"/tickets/{ticket_id}", json={"status": "Resolved"})
    assert response.status_code == 422


def test_dashboard_counts_new_ticket(client, requester):
    before = client.get("/dashboard/summary").json()["by_status"]["New"]
    make_ticket(client, requester.id)
    after = client.get("/dashboard/summary").json()["by_status"]["New"]
    assert after == before + 1