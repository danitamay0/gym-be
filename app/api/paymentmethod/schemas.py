from core.schema import DataEnvelopeResponse
from marshmallow import Schema
from marshmallow import Schema, fields


class PaymentMethodSchema(Schema):
    id = fields.UUID()
    tipo = fields.String(required=True)

