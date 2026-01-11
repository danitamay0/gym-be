# routes/sales.py
from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from app import db
from models.index import Membresia, MembresiaCliente, Venta, DetalleVenta, Inventario, Producto
from rebar import registry

import pytz
from flask import request
from sqlalchemy import and_
from datetime import datetime

@registry.handles(
    rule="/sales",
    method="GET",
)
def get_sales():
    fecha_inicio = request.args.get("fecha_inicio")
    fecha_fin = request.args.get("fecha_fin")

    query = Venta.query.options(
        db.joinedload(Venta.detalles).joinedload(DetalleVenta.producto)
    ).order_by(Venta.fecha.desc())

    if fecha_inicio:
        try:
            fecha_inicio_dt = datetime.fromisoformat(fecha_inicio)
            query = query.filter(Venta.fecha >= fecha_inicio_dt)
        except ValueError:
            pass

    if fecha_fin:
        try:
            fecha_fin_dt = datetime.fromisoformat(fecha_fin)
            # Incluir todo el día hasta las 23:59:59
            fecha_fin_dt = fecha_fin_dt + timedelta(days=1) - timedelta(seconds=1)
            query = query.filter(Venta.fecha <= fecha_fin_dt)
        except ValueError:
            pass

    ventas = query.all()

    result = []
    for venta in ventas:
        detalles_str = ", ".join(
            f"{detalle.producto.nombre} x {detalle.cantidad}"
            for detalle in venta.detalles
        )

        result.append({
            "id": str(venta.id),
            "fecha": venta.fecha.isoformat(),
            "total": float(venta.total),
            "metodo_pago": venta.metodo_pago.tipo if venta.metodo_pago else None,
            "detalles": [
                {
                    "producto_id": str(detalle.producto_id),
                    "nombre": detalle.producto.nombre,
                    "cantidad": detalle.cantidad,
                    "precio_unitario": float(detalle.precio_unitario),
                }
                for detalle in venta.detalles
            ],
            "detalle_str": detalles_str,
        })

    return jsonify(result), 200

from datetime import datetime
import pytz
from sqlalchemy.exc import SQLAlchemyError

@registry.handles(
    rule="/sales",
    method="POST",
)
def create_sale():
    data = request.get_json()
    items = data.get("items", [])
    cliente_id = data.get("cliente_id")
    metodo_pago_id = data.get("metodo_pago_id")
    
    if not items:
        return jsonify({"error": "No hay productos en la venta"}), 400

    # Definimos la zona horaria para cualquier log o cálculo extra
    colombia_tz = pytz.timezone('America/Bogota')

    try:
        total = sum(item["cantidad"] * item["precio_unitario"] for item in items)

        # Crear la venta
        # Nota: Si tu modelo 'Venta' ya tiene el default=get_colombia_time en la columna 'created',
        # no necesitas pasar 'fecha' aquí. Si la columna se llama 'created', cámbiala abajo:
        venta = Venta(
            cliente_id=cliente_id,
            # Usamos la hora de Colombia explícitamente si prefieres no depender del default
            created=datetime.now(colombia_tz), 
            metodo_pago_id=metodo_pago_id,
            total=total,
        )
        db.session.add(venta)
        db.session.flush() 

        for item in items:
            # 1. Validar inventario primero para evitar inserts innecesarios
            inv = Inventario.query.filter_by(producto_id=item["producto_id"]).first()
            
            if not inv:
                db.session.rollback()
                return jsonify({"error": f"Producto {item['producto_id']} no existe"}), 404
            
            if inv.cantidad_disponible < item["cantidad"]:
                db.session.rollback()
                return jsonify({
                    "error": f"Stock insuficiente para el producto {item['producto_id']}. Disponible: {inv.cantidad_disponible}"
                }), 400

            # 2. Restar inventario
            inv.cantidad_disponible -= item["cantidad"]

            # 3. Crear detalle
            detalle = DetalleVenta(
                venta_id=venta.id,
                producto_id=item["producto_id"],
                cantidad=item["cantidad"],
                precio_unitario=item["precio_unitario"],
            )
            db.session.add(detalle)

        db.session.commit()
        return jsonify({
            "message": "Venta registrada correctamente", 
            "venta_id": str(venta.id)
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        # Log del error para debug en consola de Docker
        print(f"Error en Venta: {str(e)}")
        return jsonify({"error": "Error interno al procesar la transacción", "details": str(e)}), 500

from flask import request, jsonify
from sqlalchemy import func
from datetime import datetime, timedelta, timezone

@registry.handles(
    rule="/dashboard/resumen",
    method="GET",
)
def resumen_dashboard():
    start = request.args.get("fecha_inicio")
    end = request.args.get("fecha_fin")
    colombia_tz = pytz.timezone('America/Bogota')
    # Fechas UTC-aware
    if start:
        from_date = datetime.strptime(start, "%Y-%m-%d")
        from_date = colombia_tz.localize(from_date)
    else:
        # Inicio del día actual en Colombia
        now_col = datetime.now(colombia_tz)
        from_date = now_col.replace(hour=0, minute=0, second=0, microsecond=0)

    if end:
        # Fin del día: sumamos 1 día para que el "menor que" sea inclusivo hasta las 23:59:59
        to_date = datetime.strptime(end, "%Y-%m-%d")
        to_date = colombia_tz.localize(to_date) + timedelta(days=1)
    else:
        # Hasta el momento exacto de ahora en Colombia
        to_date = datetime.now(colombia_tz)

    # Ventas
    ventas_query = (
        db.session.query(DetalleVenta)
        .join(Venta, Venta.id == DetalleVenta.venta_id)
        .join(DetalleVenta.producto)
        .filter(Venta.created >= from_date, Venta.created < to_date)
    )
    ventas = ventas_query.all()

    resumen_por_producto = {}
    for d in ventas:
        key = str(d.producto_id)
        if key not in resumen_por_producto:
            resumen_por_producto[key] = {
                "producto": d.producto.nombre,
                "cantidad_total": 0,
                "subtotal": 0,
            }
        resumen_por_producto[key]["cantidad_total"] += d.cantidad
        resumen_por_producto[key]["subtotal"] += d.cantidad * float(d.precio_unitario)

    resumen_ventas = []
    total_ventas = 0
    for item in resumen_por_producto.values():
        resumen_ventas.append({
            "producto": item["producto"],
            "cantidad_total": item["cantidad_total"],
            "subtotal": round(item["subtotal"]),
        })
        total_ventas += item["subtotal"]

    # Membresías
    membresias_query = (
        db.session.query(MembresiaCliente)
        .join(Membresia, Membresia.id == MembresiaCliente.membresia_id)
        .filter(
            MembresiaCliente.created >= from_date,
            MembresiaCliente.created < to_date,
            MembresiaCliente.deleted_at == None
        )
    )
    membresias = membresias_query.all()

    resumen_membresia = {}
    for m in membresias:
        tipo = m.membresia.tipo
        if tipo not in resumen_membresia:
            resumen_membresia[tipo] = {
                "cantidad": 0,
                "subtotal": 0,
                "tipo": tipo,
            }
        resumen_membresia[tipo]["cantidad"] += 1
        resumen_membresia[tipo]["subtotal"] += float(m.precio_pagado)

    resumen_membresias = []
    total_membresias = 0
    for r in resumen_membresia.values():
        resumen_membresias.append({
            "tipo": r["tipo"],
            "cantidad": r["cantidad"],
            "subtotal": round(r["subtotal"]),
        })
        total_membresias += r["subtotal"]

    # ===== Nuevo: totales por método de pago (ventas + membresías) =====
    totales_por_metodo = {}

    # Ventas por método de pago (desde los detalles, consistente con subtotal de ventas)
    for d in ventas:
        monto = d.cantidad * float(d.precio_unitario)
        metodo = (
            (d.venta.metodo_pago.tipo if d.venta and d.venta.metodo_pago else None)
            or "desconocido"
        )
        totales_por_metodo[metodo] = totales_por_metodo.get(metodo, 0) + monto

    # Membresías por método de pago
    for m in membresias:
        monto = float(m.precio_pagado)
        metodo = (
            (m.metodo_pago.tipo if m.metodo_pago else None)
            or "desconocido"
        )
        totales_por_metodo[metodo] = totales_por_metodo.get(metodo, 0) + monto

    # Armamos el arreglo de detalles redondeado
    detalles = [{"metodo_pago": k, "total": round(v)} for k, v in totales_por_metodo.items()]

    # Asegurar que la suma de detalles coincida con total_global
    total_global = sum(item["total"] for item in detalles)

    return jsonify({
        "ventas": {
            "resumen": resumen_ventas,
            "total": round(total_ventas),
        },
        "membresias": {
            "resumen": resumen_membresias,
            "total": round(total_membresias),
        },
        "detalles": detalles,  # <-- nuevo desglose por método de pago
        "total_global": total_global,
    }), 200
