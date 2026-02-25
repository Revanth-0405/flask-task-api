from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.task import Task
from flask_jwt_extended import jwt_required, get_jwt_identity

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/', methods=['POST'])
@jwt_required()
def create_task():
    """
    Create a new task
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            title:
              type: string
              example: Finish Phase 5
            description:
              type: string
              example: Implement Swagger documentation
    responses:
      201:
        description: Task created successfully
    """
    data = request.get_json()
    user_id = get_jwt_identity()
    
    new_task = Task(
        title=data.get('title'),
        description=data.get('description'),
        user_id=user_id
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"msg": "Task created", "id": new_task.id}), 201

@tasks_bp.route('/', methods=['GET'])
@jwt_required()
def get_tasks():
    """
    Get all user tasks (with Search and Pagination)
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - name: search
        in: query
        type: string
        description: Search by title (case-insensitive)
      - name: page
        in: query
        type: integer
        default: 1
        description: Page number for pagination
    responses:
      200:
        description: List of tasks with pagination metadata
    """
    user_id = get_jwt_identity()
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 5

    query = Task.query.filter_by(user_id=user_id)
    if search:
        query = query.filter(Task.title.ilike(f'%{search}%'))

    pagination = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        "tasks": [{"id": t.id, "title": t.title, "completed": t.completed} for t in pagination.items],
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": pagination.page
    }), 200