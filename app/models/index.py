import uuid
from core.models import SoftDeleteQuery
from database import db
from datetime import datetime, date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Integer, Numeric, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship

from sqlalchemy.ext.declarative import DeclarativeMeta
import pytz

BaseModel: DeclarativeMeta = db.Model

from sqlalchemy.sql import func

def get_colombia_time():
    return datetime.now(pytz.timezone('America/Bogota'))

class TimestampModel(BaseModel):
    __abstract__ = True
    # Usamos default=get_colombia_time (sin paréntesis para que se ejecute al insertar)
    created = db.Column(db.DateTime, nullable=False, default=get_colombia_time)
    
    # Para el update, usamos la misma lógica
    updated = db.Column(db.DateTime, onupdate=get_colombia_time)
    
    deleted_at = db.Column(db.DateTime, index=True, nullable=True)

    def soft_delete(self): # Agregué 'self' que faltaba en tu código
        self.deleted_at = get_colombia_time()
        db.session.commit()


class TimestampModel(BaseModel):
    __abstract__ = True
    created = db.Column(db.DateTime, nullable=False, default=func.now())
    updated = db.Column(db.DateTime, onupdate=func.now())
    deleted_at = db.Column(db.DateTime, index=True, nullable=True)

    def soft_delete(obj):
        obj.deleted_at = func.now()
        db.session.commit()


class Producto(TimestampModel):
    __tablename__ = "producto"
    query_class = SoftDeleteQuery

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = db.Column(db.String(100), nullable=False)
    precio_venta = db.Column(db.Numeric(10, 2), nullable=False)

    entradas = db.relationship("EntradaInventario", backref="producto", lazy=True)
    inventario = db.relationship("Inventario", back_populates="producto", uselist=False)
    detalleventa = db.relationship("DetalleVenta", backref="producto", lazy=True)


class EntradaInventario(TimestampModel):
    __tablename__ = "entrada_inventario"
    query_class = SoftDeleteQuery

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    producto_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("producto.id"), nullable=False
    )
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)


class Inventario(TimestampModel):
    __tablename__ = "inventario"
    query_class = SoftDeleteQuery

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    producto_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("producto.id"), nullable=False, unique=True
    )
    cantidad_disponible = db.Column(db.Integer, nullable=False, default=0)
    producto = db.relationship("Producto", back_populates="inventario", lazy="joined")


class Cliente(TimestampModel):
    __tablename__ = "cliente"
    query_class = SoftDeleteQuery

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100))
    telefono = db.Column(db.String(15))
    fecha_nacimiento = db.Column(db.Date)

    membresias_cliente = db.relationship(
        "MembresiaCliente", backref="cliente", lazy=True
    )
    evaluaciones = db.relationship("EvaluacionCliente", backref="cliente", lazy=True)
    ventas = db.relationship("Venta", backref="cliente", lazy=True)

class Fingerprint(TimestampModel):
    __tablename__ = 'fingerprints'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column( UUID(as_uuid=True), db.ForeignKey("cliente.id"), nullable=False, unique=True )
    template_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Membresia(TimestampModel):
    __tablename__ = "membresia"
    query_class = SoftDeleteQuery
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tipo = db.Column(db.String(100), nullable=False)
    duracion_dias = db.Column(db.Integer, nullable=False)
    precio_actual = db.Column(db.Numeric(10, 2), nullable=False)

    clientes = db.relationship("MembresiaCliente", backref="membresia", lazy=True)
    

class MembresiaCliente(TimestampModel):
    __tablename__ = "membresia_cliente"
    query_class = SoftDeleteQuery

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cliente_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("cliente.id"), nullable=False
    )
    membresia_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("membresia.id"), nullable=False
    )
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    precio_pagado = db.Column(db.Numeric(10, 2), nullable=False)
    active = db.Column(db.Boolean, default=True)  # Campo para indicar si la membresía está activa 
    metodo_pago_id = db.Column(UUID(as_uuid=True), db.ForeignKey("metodo_pago.id"), nullable=True)
    metodo_pago = db.relationship("MetodoPago", back_populates="membresias")

    @property
    def active_membership(self):
        current_date = datetime.utcnow().date()
        print(f"Checking active membership for {self.cliente_id} from {self.fecha_inicio} to {self.fecha_fin}")
        print(f"Current date: {current_date}")
        return self.fecha_inicio <= current_date <= self.fecha_fin
class EvaluacionCliente(TimestampModel):
    __tablename__ = "evaluacion_cliente"
    query_class = SoftDeleteQuery

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cliente_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("cliente.id"), nullable=False
    )
    fecha = db.Column(db.Date, default=datetime.utcnow)
    peso_kg = db.Column(db.Numeric(5, 2))
    porcentaje_grasa = db.Column(db.Numeric(5, 2))
    masa_muscular = db.Column(db.Numeric(5, 2))


class Venta(TimestampModel):
    __tablename__ = "venta"
    query_class = SoftDeleteQuery

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cliente_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("cliente.id"), nullable=True
    )
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Numeric(10, 2), default=0)

    detalles = db.relationship("DetalleVenta", backref="venta", lazy=True)
    metodo_pago_id = db.Column(UUID(as_uuid=True), db.ForeignKey("metodo_pago.id"), nullable=True)
    metodo_pago = db.relationship("MetodoPago", back_populates="ventas")

class DetalleVenta(TimestampModel):
    __tablename__ = "detalle_venta"
    query_class = SoftDeleteQuery

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    venta_id = db.Column(UUID(as_uuid=True), db.ForeignKey("venta.id"), nullable=False)
    producto_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("producto.id"), nullable=False
    )
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)


class MetodoPago(TimestampModel):
    __tablename__ = "metodo_pago"
    query_class = SoftDeleteQuery

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tipo = db.Column(db.String(50), nullable=False)

    ventas = db.relationship("Venta", back_populates="metodo_pago", lazy=True)
    membresias = db.relationship("MembresiaCliente", back_populates="metodo_pago", lazy=True)
