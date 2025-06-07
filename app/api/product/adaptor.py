from models.index import Producto as Product
from database import db


def get_products():
    """
    Get all products
    """
    return Product.query.alive().all()


def get_product(id):
    """
    Get a specific product by ID
    """
    return Product.query.alive().filter_by(id=id).first_or_404()


def add_product(data):
    """
    Create a new product
    """
    product = Product(**data)
    db.session.add(product)
    db.session.commit()
    return product


def update_product(id, data):
    """
    Update a product by ID
    """
    product = get_product(id)
    for key, value in data.items():
        setattr(product, key, value)
    db.session.commit()
    return product
