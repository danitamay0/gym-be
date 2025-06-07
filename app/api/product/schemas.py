from core.schema import DataEnvelopeResponse
from marshmallow import Schema
from marshmallow import Schema, fields


class ProductSchema(Schema):
    id = fields.UUID()  # solo si tu modelo Product tiene un campo id UUID
    nombre = fields.String(required=True)
    precio_venta = fields.Decimal(as_string=True, required=True)


class ProductSchemaListResponse(DataEnvelopeResponse):
    data = fields.Nested(ProductSchema, many=True)
