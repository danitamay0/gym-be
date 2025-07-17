# api/inventory_entry/routes.py

from uuid import UUID
from rebar import registry
import flask_rebar

from api.inventory_entry.adaptor import (
    get_entries,
    get_entry,
    add_entry,
    update_entry,
)
from api.inventory_entry.schemas import (
    EntradaInventarioSchema,
    EntradaInventarioListResponse
)


@registry.handles(
    rule="/inventory-entries",
    method="GET",
    response_body_schema=EntradaInventarioListResponse()
)
def list_entries():
    return get_entries()


@registry.handles(
    rule="/inventory-entries/<uuid:id>",
    method="GET",
    response_body_schema=EntradaInventarioSchema()
)
def retrieve_entry(id: UUID):
    return get_entry(id)


@registry.handles(
    rule="/inventory-entries/<uuid:id>",
    method="DELETE",
)
def delete_entry(id: UUID):
    entry = get_entry(id)
    entry.soft_delete()
    return {"message": "entry deleted"}, 200


@registry.handles(
    rule="/inventory-entries",
    method="POST",
    request_body_schema=EntradaInventarioSchema(),
    response_body_schema={201: EntradaInventarioSchema()}
)
def create_entry():
    body = flask_rebar.get_validated_body()
    entry = add_entry(body)
    return entry, 201


@registry.handles(
    rule="/inventory-entries/<uuid:id>",
    method="PUT",
    request_body_schema=EntradaInventarioSchema(),
    response_body_schema={200: EntradaInventarioSchema()}
)
def update_entry_route(id: UUID):
    body = flask_rebar.get_validated_body()
    entry = update_entry(id, body)
    return entry, 200
