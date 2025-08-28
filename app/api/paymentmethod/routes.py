from rebar import registry
from models.index import MetodoPago
from api.paymentmethod.schemas import PaymentMethodSchema

@registry.handles(
    rule="/payment-methods", method="GET",
    response_body_schema=PaymentMethodSchema(many=True)
)
def payment_methods():
    """
    get payment methods
    """
    return MetodoPago.query.all()

