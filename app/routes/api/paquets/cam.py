from flask import Blueprint, jsonify

cam_paq_blueprint = Blueprint('cam_paq', __name__)

@cam_paq_blueprint.route('/')
def get_cam_paq_data():
    return jsonify({"message": "Data from CAM Paquets"})
