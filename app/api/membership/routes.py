from uuid import UUID
from rebar import registry
import flask_rebar
from api.membership.adaptor import get_membership
from api.membership.adaptor import update
from api.membership.adaptor import get_memberships
from api.membership.adaptor import add_membership
from api.membership.schemas import MembershipSchemaListResponse
from api.membership.schemas import MembershipSchema


@registry.handles(
    rule="/memberships", method="GET", 
    response_body_schema=MembershipSchemaListResponse()
)
def memberships():
    """
    get memberships
    """
    return get_memberships()


@registry.handles(
    rule="/memberships/<uuid:id>",
    method="GET",
    response_body_schema=MembershipSchema(),
)
def membership(id: UUID):
    """
    get membership by id
    """
    return get_membership(id)


@registry.handles(
    rule="/memberships/<uuid:id>",
    method="DELETE",
)
def delete_membership(id: UUID):
    """
    delete membership by id
    """
    membership = get_membership(id)
    if not membership:
        return {"error": "Membership not found"}, 404

    membership.soft_delete()
    return {"message": "Membership deleted successfully"}, 200


@registry.handles(
    rule="/memberships",
    method="POST",
    request_body_schema=MembershipSchema(),
    response_body_schema={201: MembershipSchema()},
)
def create_membership():
    """
    create a new membership
    """
    body = flask_rebar.get_validated_body()
    membership = add_membership(body)
    return membership, 201


@registry.handles(
    rule="/memberships/<uuid:id>",
    method="PUT",
    request_body_schema=MembershipSchema(),
    response_body_schema={200: MembershipSchema()},
)
def update_membership(id: UUID):
    """
    update a membership by id
    """
    body = flask_rebar.get_validated_body()
    membership = update(id, body)
    return membership, 200