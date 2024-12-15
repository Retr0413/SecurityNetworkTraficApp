from flask import Blueprint, jsonify
api_bp = Blueprint('api', __name__)

@api_bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "ok"})
