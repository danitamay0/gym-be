from rebar import registry
from flask import request, jsonify
from models.index import Cliente, Fingerprint
from database import db


@registry.handles(rule="/fingerprints", method="POST")
def register_fingerprint():
    data = request.json
    print("aaaaaaaaaaaaaaaaaa--------->")
    user_id = data.get("user_id")
    template_id = data.get("template_id")

    if not user_id or not template_id:
        print("heree")

    fingerprint = Fingerprint(user_id=user_id, template_id=template_id)
    db.session.add(fingerprint)
    db.session.commit()

    return jsonify({"message": "Fingerprint registered"}), 201


@registry.handles(rule="/fingerprints/<int:template_id>/verify", method="GET")
def verify_fingerprint(template_id):
    fingerprint = Fingerprint.query.filter_by(template_id=template_id).first()
    print(f"Verifying fingerprint with template_id: {template_id}")
    if not fingerprint:
        return jsonify({"authorized": False}), 404

    cliente = Cliente.query.get(fingerprint.user_id)
    print(f"Cliente found: {cliente}")
    if not cliente:
        return jsonify({"authorized": False}), 404

    # Revisa si alguna de las membresías está activa usando la propiedad
    membresia_activa = any(m.active_membership for m in cliente.membresias_cliente)

    if membresia_activa:
        return jsonify({"authorized": True, "user_id": str(cliente.id)})

    return jsonify({"authorized": False}), 403
