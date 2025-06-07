from uuid import UUID
from rebar import registry
import flask_rebar
from api.product.adaptor import (
    get_product,
    get_products,
    add_product,
    update_product,
)
from api.product.schemas import ProductSchema, ProductSchemaListResponse


@registry.handles(
    rule="/products",
    method="GET",
    response_body_schema=ProductSchemaListResponse()
)
def products():
    """
    get products
    """
    return get_products()


@registry.handles(
    rule="/products/<uuid:id>",
    method="GET",
    response_body_schema=ProductSchema(),
)
def product(id: UUID):
    """
    get product by id
    """
    return get_product(id)


@registry.handles(
    rule="/products/<uuid:id>",
    method="DELETE",
)
def delete_product(id: UUID):
    """
    delete product by id
    """
    product = get_product(id)
    if not product:
        return {"error": "product not found"}, 404

    product.soft_delete()
    return {"message": "product deleted successfully"}, 200


@registry.handles(
    rule="/products",
    method="POST",
    request_body_schema=ProductSchema(),
    response_body_schema={201: ProductSchema()},
)
def create_product():
    """
    create a new product
    """
    body = flask_rebar.get_validated_body()
    product = add_product(body)
    return product, 201


@registry.handles(
    rule="/products/<uuid:id>",
    method="PUT",
    request_body_schema=ProductSchema(),
    response_body_schema={200: ProductSchema()},
)
def update_product_route(id: UUID):
    """
    update a product by id
    """
    body = flask_rebar.get_validated_body()
    product = update_product(id, body)
    return product, 200
