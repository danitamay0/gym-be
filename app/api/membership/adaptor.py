

from models.index import Membresia
from database import db 

def get_memberships():
    """
    get all memberships
    """
    return Membresia.query.alive().all()


def get_membership(id):
    """
    get a specific membership by id
    """
    return Membresia.query.alive().filter_by(id=id).first_or_404()

def add_membership(data):
    """
    create a new membership
    """
    membership = Membresia(**data)
    db.session.add(membership)
    db.session.commit()
    return membership


def update(id, data):
    """
    update a membership by id
    """
    membership = get_membership(id)
    for key, value in data.items():
        setattr(membership, key, value)
    db.session.commit()
    return membership