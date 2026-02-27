from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.services.task_service import TaskService
from app.schemas.task_schema import TaskSchema
from app.utils.decorators import auth_required

tasks_bp = Blueprint('tasks', __name__)
task_schema = TaskSchema()

# 5. POST /api/tasks
@tasks_bp.route('/', methods=['POST'])
@auth_required()
def create_task():
    data = request.get_json()
    errors = task_schema.validate(data)
    if errors:
        return jsonify({"error": True, "message": "Validation Error", "details": errors}), 400
    
    user_id = get_jwt_identity()
    response, status = TaskService.create_task(data, user_id)
    return jsonify(response), status

# 6. GET /api/tasks
@tasks_bp.route('/', methods=['GET'])
@auth_required()
def get_tasks():
    user_id = get_jwt_identity()
    status_filter = request.args.get('status')
    priority_filter = request.args.get('priority')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    response, status = TaskService.get_tasks(user_id, status_filter, priority_filter, page, per_page)
    return jsonify(response), status

# 7. GET /api/tasks/<task_id>
@tasks_bp.route('/<string:task_id>', methods=['GET'])
@auth_required()
def get_task(task_id):
    user_id = get_jwt_identity()
    response, status = TaskService.get_task(task_id, user_id)
    return jsonify(response), status

# 8. PATCH/PUT /api/tasks/<task_id>
@tasks_bp.route('/<string:task_id>', methods=['PUT', 'PATCH'])
@auth_required()
def update_task(task_id):
    data = request.get_json()
    
    # Assuming Marshmallow or similar; partial=True allows omitting fields during updates
    errors = task_schema.validate(data, partial=True) 
    if errors:
        return jsonify({"error": True, "message": "Validation Error", "details": errors}), 400

    user_id = get_jwt_identity()
    response, status = TaskService.update_task(task_id, user_id, data)
    return jsonify(response), status

# 9. DELETE /api/tasks/<task_id>
@tasks_bp.route('/<string:task_id>', methods=['DELETE'])
@auth_required()
def delete_task(task_id):
    user_id = get_jwt_identity()
    response, status = TaskService.delete_task(task_id, user_id)
    return jsonify(response), status