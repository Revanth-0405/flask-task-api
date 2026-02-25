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

    # get query parameters
    search = request.args.get('search')
    completed = request.args.get('completed')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # start the query for the specific user
    query = Task.query.filter_by(user_id=user_id)

    #search logic
    if search:
        query = query.filter(Task.title.ilike(f'%{search}%'))

    #filter logic
    if completed is not None:
        is_done = completed.lower() == 'true'
        query = query.filter_by(is_completed=is_done)
    
    # pagination logic
    paginated_tasks = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "tasks": [task.to_dict() for task in paginated_tasks.items],
        "total_pages": paginated_tasks.pages,
        "current_page": paginated_tasks.page,
        "total_items": paginated_tasks.total
    }), 200

@tasks_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=id, user_id=user_id).first_or_404()

    if not task:
        return jsonify({"message": "Task not found"}), 404
    
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({"message": "Task deleted"}), 200