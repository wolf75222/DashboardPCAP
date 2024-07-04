from flask import Blueprint, jsonify

denm_paq_blueprint = Blueprint('denm_paq', __name__, url_prefix='/denm')

@denm_paq_blueprint.route('/')
def get_denm_paq_data():
    return jsonify({"message": "Data from DENM Paquets"})
