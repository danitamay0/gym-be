
from flask import jsonify, request, Response
from models.index import MembresiaCliente, Membresia, Cliente, Fingerprint
from database import db
import pytz
from datetime import datetime

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


def get_whitelist_csv():
    """
    Retorna CSV con IDs de huellas (slots) de clientes con membresía ACTIVA.
    Ejemplo output: "1,5,20,44,299"
    """
    try:
        # 1. Obtener fecha actual en Colombia (para coincidir con tu lógica de modelos)
        bogota_tz = pytz.timezone('America/Bogota')
        today = datetime.now(bogota_tz).date()

        # 2. Consulta Optimizada
        # Seleccionamos solo el template_id (slot del sensor)
        # Hacemos JOIN implícito al filtrar por relaciones
        valid_slots = db.session.query(Fingerprint.template_id)\
            .join(Cliente, Fingerprint.user_id == Cliente.id)\
            .join(MembresiaCliente, Cliente.id == MembresiaCliente.cliente_id)\
            .filter(
                # Que la membresía esté marcada como activa
                MembresiaCliente.active == True,
                # Que no esté borrada (Soft Delete check)
                MembresiaCliente.deleted_at == None,
                # Que la fecha actual esté dentro del rango
                MembresiaCliente.fecha_inicio <= today,
                MembresiaCliente.fecha_fin >= today
            ).all()

        # valid_slots será una lista de tuplas: [(1,), (5,), (10,)]
        
        # 3. Aplanar lista y convertir a CSV
        # Usamos set() para evitar duplicados si un cliente tiene 2 membresías activas por error
        ids_list = [str(slot[0]) for slot in valid_slots]
        csv_response = ",".join(set(ids_list))
        
        return Response(csv_response, mimetype='text/plain', status=200)

    except Exception as e:
        print(f"Error generando whitelist: {str(e)}")
        return Response("Error interno", status=500)