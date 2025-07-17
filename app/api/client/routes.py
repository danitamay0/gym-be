from uuid import UUID
from rebar import registry
import flask_rebar
from api.client.adaptor import get_client
from api.client.adaptor import update
from api.client.adaptor import get_clients
from api.client.adaptor import add_client
from api.client.schemas import ClientSchemaListResponse
from api.client.schemas import ClientSchema
from api.client.schemas import ClientQueryParams


@registry.handles(
    rule="/clients", method="GET",
    query_string_schema=ClientQueryParams,
    response_body_schema=ClientSchemaListResponse()
)
def clients():
    """
    get clients
    """
    query_params = flask_rebar.get_validated_args()
    search = query_params.get("search")

    return get_clients(search=search)


@registry.handles(
    rule="/clients/<uuid:id>",
    method="GET",
    response_body_schema=ClientSchema(),
)
def client(id: UUID):
    """
    get client by id
    """
    return get_client(id)


@registry.handles(
    rule="/clients/<uuid:id>",
    method="DELETE",
)
def delete_client(id: UUID):
    """
    delete client by id
    """
    client = get_client(id)
    if not client:
        return {"error": "client not found"}, 404

    client.soft_delete()
    return {"message": "client deleted successfully"}, 200


@registry.handles(
    rule="/clients",
    method="POST",
    request_body_schema=ClientSchema(),
    response_body_schema={201: ClientSchema()},
)
def create_client():
    """
    create a new client
    """
    body = flask_rebar.get_validated_body()
    client = add_client(body)
    return client, 201


@registry.handles(
    rule="/clients/<uuid:id>",
    method="PUT",
    request_body_schema=ClientSchema(),
    response_body_schema={200: ClientSchema()},
)
def update_client(id: UUID):
    """
    update a client by id
    """
    body = flask_rebar.get_validated_body()
    client = update(id, body)
    return client, 200