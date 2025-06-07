from core.schema import DataEnvelopeResponse
from marshmallow import Schema
from marshmallow import Schema, fields


class ClientSchema(Schema):
    id = fields.UUID()
    nombre = fields.String(required=True)
    correo = fields.String()
    telefono = fields.String()
    fecha_nacimiento = fields.Date()


class ClientSchemaListResponse(DataEnvelopeResponse):
    data = fields.Nested(ClientSchema, many=True)
