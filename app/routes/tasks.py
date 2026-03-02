from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.services.task_service import TaskService
from app.schemas.task_schema import TaskSchema
from app.utils.decorators import auth_required
from app.services.dynamodb_service import dynamo_service
from collections import Counter

tasks_bp = Blueprint('tasks', __name__)
task_schema = TaskSchema()

@tasks_bp.route('/stats', methods=['GET'])
@auth_required()
def get_stats():
    user_id = get_jwt_identity()
    response, status = TaskService.get_task_stats(user_id)
    return jsonify(response), status

@tasks_bp.route('/search', methods=['GET'])
@auth_required()
def search_tasks():
    user_id = get_jwt_identity()
    search_term = request.args.get('q', '')
    response, status = TaskService.search_tasks(user_id, search_term)
    return jsonify(response), status

@tasks_bp.route('/bulk-update', methods=['POST'])
@auth_required()
def bulk_update():
    user_id = get_jwt_identity()
    data = request.get_json()
    response, status = TaskService.bulk_update_tasks(user_id, data)
    return jsonify(response), status

@tasks_bp.route('/bulk-delete', methods=['POST'])
@auth_required()
def bulk_delete():
    user_id = get_jwt_identity()
    data = request.get_json()
    response, status = TaskService.bulk_delete_tasks(user_id, data)
    return jsonify(response), status

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

activities_bp = Blueprint('activities', __name__)

@activities_bp.route('/', methods=['GET'])
@auth_required()
def get_activities():
    user_id = get_jwt_identity()
    action = request.args.get('action')
    task_id = request.args.get('task_id')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    activities = dynamo_service.get_activities(user_id, action, task_id, date_from, date_to)
    return jsonify({"activities": activities}), 200

@activities_bp.route('/summary', methods=['GET'])
@auth_required()
def get_activity_summary():
    user_id = get_jwt_identity()
    activities = dynamo_service.get_activities(user_id)
    
    # Generate summary counts based on action types
    action_counts = dict(Counter([item.get('action') for item in activities]))
    
    return jsonify({
        "total_activities": len(activities),
        "summary": action_counts
    }), 200