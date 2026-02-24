from flask import Blueprint, jsonify
from app.extensions import db
from sqlalchemy import text

health_bp = Blueprint('health', __name__)

@health_bp.route('/', methods=['GET'])
def health_check():
    db_status = "ok"
    try:
        # Check PostgreSQL connection
        db.session.execute(text('SELECT 1'))
    except Exception as e:
        db_status = f"failed: {str(e)}"
        
    return jsonify({
        "status": "up",
        "database_connectivity": db_status
    }), 200