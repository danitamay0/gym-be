from uuid import UUID
from rebar import registry
import flask_rebar
from api.membership_client.adaptor import (
    add_membership_client,
    get_memberships,
    get_memberships_client
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


@registry.handles(rule='/memberships-clients', method='GET')
def get_membresias():
    return get_memberships()

@registry.handles(
    rule="/memberships-client/<uuid:id>",
    method="DELETE",
)
def delete_membership_client(id: UUID):
    """
    delete membership by id
    """
    membership = get_memberships_client(id)
    if not membership:
        return {"error": "membership not found"}, 404

    membership.soft_delete()
    return {"message": "membership deleted successfully"}, 200
