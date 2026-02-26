from flask import Blueprint, jsonify
from app.extensions import db
import sqlalchemy

health_bp = Blueprint('health', __name__)

@health_bp.route('/', methods=['GET'])
def health_check():
    health_status = {"status": "healthy", "database": "disconnected"}
    try:
        db.session.execute(sqlalchemy.text('SELECT 1'))
        health_status["database"] = "connected"
        return jsonify(health_status), 200
    except Exception as e:
        health_status["status"] = "unhealthy"
        return jsonify(health_status), 503