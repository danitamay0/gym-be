

# api/inventory/adaptor.py

from models.index import Inventario
from database import db

def get_inventories():
    return Inventario.query.options(db.joinedload(Inventario.producto)).alive().all()


def get_inventory(id):
    return Inventario.query.options(db.joinedload(Inventario.producto)).alive().filter_by(id=id).first_or_404()


def add_inventory(data):
    inventory = Inventario(**data)
    db.session.add(inventory)
    db.session.commit()
    return inventory


def update_inventory(id, data):
    inventory = get_inventory(id)
    for key, value in data.items():
        setattr(inventory, key, value)
    db.session.commit()
    return inventory
