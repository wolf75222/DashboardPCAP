from flask import Blueprint, jsonify

denm_blueprint = Blueprint('denm', __name__)

@denm_blueprint.route('/')
def get_denm_data():
    return jsonify({"message": "Data from DENM"})
