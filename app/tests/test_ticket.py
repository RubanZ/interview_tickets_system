import pytest
from app.main import app, db


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    with app.app_context():
        db.create_all()

    with app.test_client() as client:
        yield client

    with app.app_context():
        db.session.remove()
        db.drop_all()


def test_get_tickets(client):
    response = client.get("/tickets/")
    assert response.status_code == 200
    assert response.json == {"total": 0, "items": []}
    

def test_create_ticket(client):
    response = client.post("/tickets/", json={"subject": "Test", "text": "Test", "email": "test@mail.ru"})
    assert response.status_code == 201
    assert response.json['id'] == 1
    assert response.json['subject'] == "Test"
    assert response.json['text'] == "Test"
    assert response.json['email'] == "test@mail.ru"
    assert response.json['status'] == "open"
    assert response.json['comments'] == []

    response = client.get("/tickets/")
    assert response.status_code == 200
    assert response.json["total"] == 1
    assert len(response.json["items"]) == 1
    
def test_add_comment(client):
    response = client.post("/tickets/", json={"subject": "Test", "text": "Test", "email": "Test@mail.ru"})
    assert response.status_code == 201
    
    response = client.post(f"/tickets/{response.json['id']}/comments", 
                           json={"text": "Test message", "email": "test@mail.ru"})
    
    assert response.status_code == 201
    assert response.json['id'] == 1
    assert response.json['text'] == "Test message"
    assert response.json['email'] == "test@mail.ru"
    

def test_update_ticket_status_closed(client):
    responseTicket = client.post("/tickets/", json={"subject": "Test", "text": "Test", "email": "test@mail.ru"})
    assert responseTicket.status_code == 201
    
    # Из открытого в отвечен
    response = client.put(f"/tickets/{responseTicket.json['id']}", json={"status": "closed"})
    
    assert response.status_code == 200
    assert response.json['status'] == "closed"
    
    # Изменение статуса закрытого тикета
    response = client.put(f"/tickets/{responseTicket.json['id']}", json={"status": "waiting_for_answer"})
    assert response.status_code == 400
    


def test_update_ticket_status_changes(client):
    responseTicket = client.post("/tickets/", json={"subject": "Test", "text": "Test", "email": "test@mail.ru"})
    assert responseTicket.status_code == 201

    # Из открытого в waiting_for_answer
    response = client.put(f"/tickets/{responseTicket.json['id']}", json={"status": "waiting_for_answer"})
    assert response.status_code == 400
    # Из открытого в answered
    response = client.put(f"/tickets/{responseTicket.json['id']}", json={"status": "answered"})
    assert response.status_code == 200
    
    # Из answered в waiting_for_answer
    response = client.put(f"/tickets/{responseTicket.json['id']}", json={"status": "waiting_for_answer"})
    assert response.status_code == 200
    
    # Из waiting_for_answer в open
    response = client.put(f"/tickets/{responseTicket.json['id']}", json={"status": "open"})
    assert response.status_code == 400
    
    # Из waiting_for_answer в closed
    response = client.put(f"/tickets/{responseTicket.json['id']}", json={"status": "closed"})
    assert response.status_code == 200
    

def test_add_comment_to_closed_ticket(client):
    responseTicket = client.post("/tickets/", json={"subject": "Test", "text": "Test", "email": "test@mail.ru"})
    assert responseTicket.status_code == 201
    
    response = client.put(f"/tickets/{responseTicket.json['id']}", json={"status": "closed"})
    assert response.status_code == 200
    
    response = client.post(f"/tickets/{responseTicket.json['id']}/comments",
                            json={"text": "Test message", "email": "test@mail.ru"})
    assert response.status_code == 400
    
    
def test_get_ticket_paginate(client):
    for i in range(1, 6):
        response = client.post("/tickets/", json={"subject": f"Test {i}", "text": f"Test {i}", "email": "test@mail.ru"})
        assert response.status_code == 201
    
    response = client.get("/tickets/?page=1&page_size=2")
    assert response.status_code == 200
    assert response.json["total"] == 5
    assert len(response.json["items"]) == 2
    
    # Проверка пагинации за пределами
    response = client.get("/tickets/?page=4&page_size=2")
    assert response.status_code == 404
    
    response = client.get("/tickets/?page=-2&page_size=-210")
    assert response.status_code == 400
    

def test_add_comment_in_different_status_tickets(client):
    responseTicket = client.post("/tickets/", json={"subject": "Test", "text": "Test", "email": "test@mail.ru"})
    assert responseTicket.status_code == 201

    response = client.post(f"/tickets/{responseTicket.json['id']}/comments",
                           json={"text": "Test message", "email": "test@mail.ru"})

    assert response.status_code == 201

    response = client.put(f"/tickets/{responseTicket.json['id']}", json={"status": "answered"})
    assert response.status_code == 200
    
    response = client.post(f"/tickets/{responseTicket.json['id']}/comments",
                            json={"text": "Test message", "email": "Another@mail.ru"})
    assert response.status_code == 201

    response = client.put(f"/tickets/{responseTicket.json['id']}", json={"status": "waiting_for_answer"})
    assert response.status_code == 200
    
    response = client.post(f"/tickets/{responseTicket.json['id']}/comments",
                           json={"text": "Test message", "email": "test@mail.ru"})
    assert response.status_code == 201
    
    response = client.put(f"/tickets/{responseTicket.json['id']}", json={"status": "closed"})
    assert response.status_code == 200

    response = client.post(f"/tickets/{responseTicket.json['id']}/comments",
                           json={"text": "END message", "email": "Another@mail.ru"})
    assert response.status_code == 400