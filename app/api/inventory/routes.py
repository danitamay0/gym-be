from uuid import UUID
from rebar import registry
import flask_rebar

from api.inventory.adaptor import (
    get_inventories,
    get_inventory,
    add_inventory,
    update_inventory,
)
from api.inventory.schemas import InventarioSchema, InventarioListResponse


@registry.handles(
    rule="/inventories",
    method="GET",
    response_body_schema=InventarioListResponse()
)
def list_inventories():
    return get_inventories()


@registry.handles(
    rule="/inventories/<uuid:id>",
    method="GET",
    response_body_schema=InventarioSchema()
)
def retrieve_inventory(id: UUID):
    return get_inventory(id)




@registry.handles(
    rule="/inventories/<uuid:id>",
    method="PUT",
    request_body_schema=InventarioSchema(),
    response_body_schema={200: InventarioSchema()}
)
def update_inventory_route(id: UUID):
    body = flask_rebar.get_validated_body()
    inventory = update_inventory(id, body)
    return inventory, 200
