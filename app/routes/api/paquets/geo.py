from flask import Blueprint, jsonify

geo_paq_blueprint = Blueprint('geo_paq', __name__, url_prefix='/geo')

@geo_paq_blueprint.route('/')
def get_geo_paq_data():
    return jsonify({"message": "Data from GEO Paquets"})
