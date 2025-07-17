# schemas/entrada_inventario.py

from marshmallow import Schema, fields
from core.schema import DataEnvelopeResponse

class EntradaInventarioSchema(Schema):
    id = fields.UUID(dump_only=True)
    producto_id = fields.UUID(required=True)
    cantidad = fields.Integer(required=True)
    precio_unitario = fields.Decimal(as_string=True, required=True)
    fecha = fields.DateTime(dump_only=True)


class EntradaInventarioListResponse(DataEnvelopeResponse):
    class Schema(Schema):
        data = fields.List(fields.Nested(EntradaInventarioSchema))