

from models.index import Membresia
from database import db 

def get_memberships():
    """
    get all memberships
    """
    return Membresia.query.alive().all()


def get_membership(id):
    """
    get a specific membership by id
    """
    return Membresia.query.alive().filter_by(id=id).first_or_404()

def add_membership(data):
    """
    create a new membership
    """
    membership = Membresia(**data)
    db.session.add(membership)
    db.session.commit()
    return membership


def update(id, data):
    """
    update a membership by id
    """
    membership = get_membership(id)
    for key, value in data.items():
        setattr(membership, key, value)
    db.session.commit()
    return membership


from flask import Flask, request, jsonify
from pyfingerprint.pyfingerprint import PyFingerprint
import psycopg2

app = Flask(__name__)

@app.route('/capture-fingerprint', methods=['POST'])
def capture_fingerprint():
    """ user_id = request.args.get("user_id")
    if not user_id:
        return jsonify(success=False, message="Falta user_id"), 400 """

    try:
        # Inicializa el lector (ajusta el puerto si es necesario)
        f = PyFingerprint('/dev/ttyUSB0', 57600)
        if not f.verifyPassword():
            return jsonify(success=False, message="Lector no verificado")

        # Espera la huella
        print("Esperando huella...")
        while not f.readImage():
            pass

        f.convertImage(0x01)
        template = f.downloadCharacteristics(0x01)
        template_str = str(template)
        print("Huella capturada:", template_str)
        # Guarda en la base de datos
        """ conn = psycopg2.connect("dbname=tu_db user=tu_user password=tu_pass")
        cur = conn.cursor()
        cur.execute("INSERT INTO fingerprints (user_id, template) VALUES (%s, %s)", (user_id, template_str))
        conn.commit()
        cur.close()
        conn.close()
        """
        return jsonify(success=True)

    except Exception as e:
        return jsonify(success=False, message=str(e)), 500
