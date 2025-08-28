
from flask import jsonify, request
from models.index import MembresiaCliente, Membresia, Cliente
from database import db

def get_memberships_client(id):
    """
    Get a specific membership by ID
    """
    return MembresiaCliente.query.alive().filter_by(id=id).first_or_404()


def add_membership_client(data):
    cliente_id = data.get("cliente_id")  # Asumiendo que el cliente_id está en los datos
    db.session.query(MembresiaCliente).filter(
        MembresiaCliente.cliente_id == cliente_id,
        MembresiaCliente.active == True  # Solo desactivar las activas
    ).update({"active": False}, synchronize_session=False)
    mc = MembresiaCliente(**data)
    db.session.add(mc)
    db.session.commit()
    return mc

def get_memberships():
    # Obtener el nombre del cliente desde los parámetros de consulta (query parameters)
    nombre_cliente = request.args.get('search', default='', type=str)

    # Construir la consulta
    membresias_query = db.session.query(MembresiaCliente, Cliente, Membresia).join(Cliente).join(Membresia)
    
    # Filtrar por nombre del cliente si se proporciona
    if nombre_cliente:
        membresias_query = membresias_query.filter(Cliente.nombre.ilike(f"%{nombre_cliente}%"))

    # Ordenar por fecha de creación de la membresía
    membresias = membresias_query.order_by(MembresiaCliente.created.desc()).all()

    # Formateamos la respuesta
    result = []
    for membresia_cliente, cliente, membresia in membresias:
        result.append({
            'cliente': {
                'id': cliente.id,
                'nombre': cliente.nombre,
                'correo': cliente.correo,
                'telefono': cliente.telefono
            },
            'membresia': {
                'id': membresia.id,
                'tipo': membresia.tipo,
                'duracion_dias': membresia.duracion_dias,
                'precio_actual': str(membresia.precio_actual)
            },
            'membresia_cliente': {
                'id': membresia_cliente.id,
                'fecha_inicio': str(membresia_cliente.fecha_inicio),
                'fecha_fin': str(membresia_cliente.fecha_fin),
                'precio_pagado': str(membresia_cliente.precio_pagado),
                'deleted': membresia_cliente.deleted_at
            }
        })
    
    return jsonify(result)