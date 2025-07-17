from marshmallow import Schema, fields
from core.schema import DataEnvelopeResponse
from api.membership.schemas import MembershipSchema


class MembershipClientSchema(Schema):
    id = fields.UUID(dump_only=True)
    cliente_id = fields.UUID(dump_only=True)

    membresia_id = fields.UUID(required=True)
    fecha_inicio = fields.Date(required=True)
    fecha_fin = fields.Date(required=True)
    precio_pagado = fields.Decimal(as_string=True, required=True)

    membresia = fields.Nested(MembershipSchema, dump_only=True)
    active_membership = fields.Boolean(dump_only=True)


class MembershipClientCreateSchema(Schema):
    cliente_id = fields.UUID(required=True)
    membresia_id = fields.UUID(required=True)
    fecha_inicio = fields.Date(required=True)
    fecha_fin = fields.Date(required=True)
    precio_pagado = fields.Decimal(as_string=True, required=True)


class MembershipClientListResponse(DataEnvelopeResponse):
    class Schema(Schema):
        data = fields.List(fields.Nested(MembershipClientSchema))
