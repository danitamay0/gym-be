from api.membership.routes import memberships 
from api.membership.routes import membership
from api.membership.routes import create_membership
from api.membership.routes import update_membership

from api.client.routes import create_client
from api.client.routes import update_client
from api.client.routes import get_clients
from api.client.routes import get_client

from api.product.routes import create_product
from api.product.routes import update_product
from api.product.routes import get_products
from api.product.routes import get_product

from api.inventory_entry.routes import list_entries
from api.inventory_entry.routes import retrieve_entry
from api.inventory_entry.routes import create_entry
from api.inventory_entry.routes import delete_entry
from api.inventory_entry.routes import update_entry

from api.inventory.routes import list_inventories

from api.membership_client.routes import create_membresia_cliente
from api.fingerprint.routes import verify_fingerprint
from api.fingerprint.routes import register_fingerprint

from api.esp32.routes import get_esp32_ip
from api.sell.routes import create_sale
from api.sell.routes import get_sales
from api.sell.routes import resumen_dashboard