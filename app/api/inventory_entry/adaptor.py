# api/inventory_entry/adaptor.py

from models.index import EntradaInventario, Inventario
from database import db


def get_entries():
    return EntradaInventario.query.alive().all()


def get_entry(id):
    return EntradaInventario.query.alive().filter_by(id=id).first_or_404()


def add_entry(data):
    producto_id = data["producto_id"]
    cantidad = data["cantidad"]

    entry = EntradaInventario(**data)
    db.session.add(entry)

    inventario = Inventario.query.filter_by(producto_id=producto_id).first()
    if inventario:
        inventario.cantidad_disponible += cantidad
    else:
        inventario = Inventario(producto_id=producto_id, cantidad_disponible=cantidad)
        db.session.add(inventario)

    db.session.commit()
    return entry


def update_entry(id, data):
    entry = get_entry(id)
    for key, value in data.items():
        setattr(entry, key, value)
    db.session.commit()
    return entry
