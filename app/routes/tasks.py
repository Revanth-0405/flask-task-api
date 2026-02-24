from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.task import Task

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/', methods=['POST'])
@jwt_required() # <--- Only logged-in users can enter
def create_task():
    user_id = get_jwt_identity() # Extracts the UUID from the token
    data = request.get_json()
    
    new_task = Task(
        title=data.get('title'),
        description=data.get('description'),
        user_id=user_id # Automatically links the task to the current user
    )
    
    db.session.add(new_task)
    db.session.commit()
    
    return jsonify(new_task.to_dict()), 201

@tasks_bp.route('/', methods=['GET'])
@jwt_required()
def get_user_tasks():
    user_id = get_jwt_identity()
    # Only fetch tasks belonging to THIS user
    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify([task.to_dict() for task in tasks]), 200