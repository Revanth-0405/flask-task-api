from app.extensions import db
from app.models.task import Task
from app.services.dynamodb_service import dynamo_service

class TaskService:
    @staticmethod
    def create_task(data, user_id):
        new_task = Task(
            title=data['title'],
            description=data.get('description'),
            status=data.get('status', 'todo'),
            priority=data.get('priority', 'medium'),
            due_date=data.get('due_date'),
            user_id=user_id
        )
        db.session.add(new_task)
        db.session.commit()
        
        # Log activity to DynamoDB
        dynamo_service.log_activity(user_id, "create", new_task.id, {"title": new_task.title})
        return new_task.to_dict(), 201

    @staticmethod
    def get_tasks(user_id, status, priority, page, per_page):
        query = Task.query.filter_by(user_id=user_id, is_active=True)
        
        if status: query = query.filter_by(status=status)
        if priority: query = query.filter_by(priority=priority)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            "tasks": [task.to_dict() for task in pagination.items],
            "meta": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "total_pages": pagination.pages
            }
        }, 200

    @staticmethod
    def get_task(task_id, user_id):
        task = Task.query.filter_by(id=task_id, user_id=user_id, is_active=True).first()
        if not task:
            return {"error": True, "message": "Task not found or unauthorized", "details": {}}, 404
        return task.to_dict(), 200

    @staticmethod
    def update_task(task_id, user_id, data):
        task = Task.query.filter_by(id=task_id, user_id=user_id, is_active=True).first()
        if not task:
            return {"error": True, "message": "Task not found or unauthorized", "details": {}}, 404

        if 'title' in data: task.title = data['title']
        if 'description' in data: task.description = data['description']
        if 'status' in data: task.status = data['status']
        if 'priority' in data: task.priority = data['priority']
        if 'due_date' in data: task.due_date = data['due_date']

        db.session.commit()
        
        # Log activity to DynamoDB
        dynamo_service.log_activity(user_id, "update", task.id, data)
        return task.to_dict(), 200

    @staticmethod
    def delete_task(task_id, user_id):
        task = Task.query.filter_by(id=task_id, user_id=user_id, is_active=True).first()
        if not task:
            return {"error": True, "message": "Task not found or unauthorized", "details": {}}, 404

        task.is_active = False
        db.session.commit()
        
        # Log activity to DynamoDB
        dynamo_service.log_activity(user_id, "delete", task.id, {})
        return {"message": "Task soft deleted successfully"}, 200