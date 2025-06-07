from core.schema import DataEnvelopeResponse
from marshmallow import Schema
from marshmallow import Schema, fields


class MembershipSchema(Schema):
    id = fields.UUID()
    tipo = fields.String(required=True)
    duracion_dias = fields.Integer(required=True)
    precio_actual = fields.Integer(required=True)


class MembershipSchemaListResponse(DataEnvelopeResponse):
    data = fields.Nested(MembershipSchema, many=True)