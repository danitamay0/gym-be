

from models.index import Cliente
from database import db 


def get_clients():
    """
    get all clients
    """
    return Cliente.query.alive().all()


def get_client(id):
    """
    get a specific client by id
    """
    return Cliente.query.alive().filter_by(id=id).first_or_404()


def add_client(data):
    """
    create a new client
    """
    client = Cliente(**data)
    db.session.add(client)
    db.session.commit()
    return client


def update(id, data):
    """
    update a client by id
    """
    client = get_client(id)
    for key, value in data.items():
        setattr(client, key, value)
    db.session.commit()
    return client