# routes/sales.py
from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from app import db
from models.index import Membresia, MembresiaCliente, Venta, DetalleVenta, Inventario, Producto
from rebar import registry


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
    )

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


@registry.handles(
    rule="/sales",
    method="POST",
)
def create_sale():
    data = request.get_json()
    items = data.get("items", [])
    cliente_id = data.get("cliente_id", None)

    if not items:
        return jsonify({"error": "No hay productos en la venta"}), 400

    try:
        total = sum(item["cantidad"] * item["precio_unitario"] for item in items)

        # Crear la venta
        venta = Venta(
            cliente_id=cliente_id,
            fecha=datetime.utcnow(),
            total=total,
        )
        db.session.add(venta)
        db.session.flush()  # para obtener venta.id

        # Crear detalles y actualizar inventario
        for item in items:
            detalle = DetalleVenta(
                venta_id=venta.id,
                producto_id=item["producto_id"],
                cantidad=item["cantidad"],
                precio_unitario=item["precio_unitario"],
            )
            db.session.add(detalle)

            # Restar del inventario
            inv = Inventario.query.filter_by(producto_id=item["producto_id"]).first()
            if not inv:
                db.session.rollback()
                return jsonify({"error": "Producto no encontrado en inventario"}), 404
            if inv.cantidad_disponible < item["cantidad"]:
                db.session.rollback()
                return jsonify({
                    "error": f"No hay suficiente inventario para el producto {item['producto_id']}"
                }), 400

            inv.cantidad_disponible -= item["cantidad"]

        db.session.commit()
        return jsonify({"message": "Venta registrada correctamente", "venta_id": str(venta.id)}), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Error al registrar la venta", "details": str(e)}), 500


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

    # Fechas UTC-aware
    if start:
        from_date = datetime.strptime(start, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    else:
        from_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)

    if end:
        # Usamos el inicio del día siguiente como exclusivo para que fin sea inclusivo
        to_date = datetime.strptime(end, "%Y-%m-%d").replace(tzinfo=timezone.utc) + timedelta(days=1)
    else:
        to_date = datetime.utcnow().replace(tzinfo=timezone.utc)

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
        .filter(MembresiaCliente.created >= from_date, MembresiaCliente.created < to_date,
           MembresiaCliente.deleted_at == None )
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

    return jsonify({
        "ventas": {
            "resumen": resumen_ventas,
            "total": round(total_ventas),
        },
        "membresias": {
            "resumen": resumen_membresias,
            "total": round(total_membresias),
        },
        "total_global": round(total_ventas + total_membresias),
    }), 200
