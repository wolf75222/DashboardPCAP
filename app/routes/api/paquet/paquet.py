from flask import Blueprint, jsonify

paquet_blueprint = Blueprint('paquet', __name__)

@paquet_blueprint.route('/')
def get_paquet_data():
    return jsonify({"message": "Data from Paquet"})


