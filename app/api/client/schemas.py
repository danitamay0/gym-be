from api.membership_client.schemas import MembershipClientSchema
from core.schema import DataEnvelopeResponse
from marshmallow import Schema
from marshmallow import Schema, fields
from flask_rebar import RequestSchema

class ClientQueryParams(RequestSchema):
    search = fields.String(required=False)
    
class ClientSchema(Schema):
    id = fields.UUID()
    nombre = fields.String(required=True)
    correo = fields.String()
    telefono = fields.String()
    fecha_nacimiento = fields.Date()
    last_membership = fields.Nested(MembershipClientSchema, dump_only=True)
    membership = fields.Nested(MembershipClientSchema, required=False)

class ClienFulltSchema(Schema):
    id = fields.UUID()
    nombre = fields.String(required=True)
    correo = fields.String()
    telefono = fields.String()
    fecha_nacimiento = fields.Date()
    last_membership = fields.Nested(MembershipClientSchema, dump_only=True)
    membership = fields.Nested(MembershipClientSchema, required=False)
    fingerprint = fields.String(dump_only=True)


class ClientSchemaListResponse(DataEnvelopeResponse):
    data = fields.Nested(ClienFulltSchema, many=True)
