

from models.index import Cliente, MembresiaCliente
from database import db
from sqlalchemy import or_

from datetime import date
from sqlalchemy import or_

def get_clients(search: str = None):
    """
    Get all clients, including their last membership and active status.
    Ordered by:
    1. Not expired first, then expired
    2. Among not expired: closest to expire first
       Among expired: most recently expired first
    """
    query = Cliente.query.alive()
    if search:
        query = query.filter(
            or_(
                Cliente.nombre.ilike(f"%{search}%"),
                Cliente.telefono.ilike(f"%{search}%")
            )
        )

    clientes = query.all()

    no_vencidos = []
    vencidos = []

    for cliente in clientes:
        last_membership = (
            MembresiaCliente.query
            .filter_by(cliente_id=cliente.id)
            .filter(MembresiaCliente.active == True,
             MembresiaCliente.deleted_at == None)
            .order_by(MembresiaCliente.created.desc())
            .first()
        )

        cliente.last_membership = last_membership

        if last_membership and last_membership.fecha_fin:
            if last_membership.fecha_fin >= date.today():
                no_vencidos.append(cliente)
            else:
                vencidos.append(cliente)
        else:
            # sin membresía o sin fecha_fin se considera vencido
            vencidos.append(cliente)

    # Ordenar cada grupo
    no_vencidos.sort(key=lambda c: c.last_membership.fecha_fin if c.last_membership and c.last_membership.fecha_fin else date.max)
    vencidos.sort(key=lambda c: c.last_membership.fecha_fin if c.last_membership and c.last_membership.fecha_fin else date.min, reverse=True)

    # Combinar la lista final
    return no_vencidos + vencidos



def get_client(id):
    """
    get a specific client by id
    """
    cliente = Cliente.query.alive().filter_by(id=id).first_or_404()

    # Cargar la última membresía activa
    ultima_membresia = (    
        MembresiaCliente.query
        .filter_by(cliente_id=id)
        .order_by(MembresiaCliente.fecha_inicio.desc())
        .first()
    )

    # Asociar manualmente para que el schema lo serialice
    cliente.last_membership = ultima_membresia
    return cliente


def add_client(data):
    """
    Create a new client and assign an initial membership
    """
    # Extraer los datos de la membresía
    membership_data = data.pop("membership", None)

    # Crear cliente
    client = Cliente(**data)
    db.session.add(client)
    db.session.flush()  # Para obtener el ID antes del commit

    # Crear la membresía si viene en el payload
    if membership_data:
        membership_data["cliente_id"] = client.id
        mc = MembresiaCliente(**membership_data)
        db.session.add(mc)

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