from flask import Blueprint, jsonify

cam_blueprint = Blueprint('cam', __name__)

@cam_blueprint.route('/')
def get_cam_data():
    return jsonify({"message": "Data from CAM"})
