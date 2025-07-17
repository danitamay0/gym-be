from rebar import registry
import flask_rebar
from api.membership_client.adaptor import (
    add_membership_client,
)
from api.membership_client.schemas import MembershipClientSchema, MembershipClientCreateSchema


@registry.handles(
    rule="/membership-clients",
    method="POST",
    request_body_schema=MembershipClientCreateSchema(),
    response_body_schema={201: MembershipClientSchema()},
)
def create_membresia_cliente():
    body = flask_rebar.get_validated_body()
    mc = add_membership_client(body)
    return mc, 201
