from flask import Blueprint, jsonify

geo_blueprint = Blueprint('geo', __name__)

@geo_blueprint.route('/')
def get_geo_data():
    return jsonify({"message": "Data from GEO"})
