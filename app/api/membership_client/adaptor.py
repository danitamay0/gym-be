

from models.index import MembresiaCliente
from database import db

def add_membership_client(data):
    mc = MembresiaCliente(**data)
    db.session.add(mc)
    db.session.commit()
    return mc
