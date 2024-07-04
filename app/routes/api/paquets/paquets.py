from flask import Blueprint, jsonify

paquets_blueprint = Blueprint('paquets', __name__, url_prefix='/paquets')

@paquets_blueprint.route('/')
def get_paquets_data():
    return jsonify({"message": "General data from all Paquets"})
