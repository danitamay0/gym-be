# schemas/inventario.py

from marshmallow import Schema, fields
from api.product.schemas import ProductSchema
from core.schema import DataEnvelopeResponse


class InventarioSchema(Schema):
    id = fields.UUID(dump_only=True)
    producto_id = fields.UUID(required=True)
    cantidad_disponible = fields.Integer(required=True)

    producto = fields.Nested(ProductSchema, dump_only=True)  # ← aquí incluimos el producto


class InventarioListResponse(DataEnvelopeResponse):
    data = fields.List(fields.Nested(InventarioSchema))
