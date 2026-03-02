from flask import request
from sqlalchemy import or_, func
from app.extensions import db
from app.models.task import Task
from app.services.dynamodb_service import dynamo_service

class TaskService:
    @staticmethod
    def _get_ip():
        """Dynamically fetches the real IP address instead of hardcoding 127.0.0.1"""
        if request and request.remote_addr:
            return request.remote_addr
        return '127.0.0.1'
    
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
    
     @staticmethod
    def get_task_stats(user_id):
        """Generates statistical summary of user's active tasks"""
        total_tasks = Task.query.filter_by(user_id=user_id, is_active=True).count()
        status_counts = db.session.query(Task.status, func.count(Task.id)).filter_by(user_id=user_id, is_active=True).group_by(Task.status).all()
        priority_counts = db.session.query(Task.priority, func.count(Task.id)).filter_by(user_id=user_id, is_active=True).group_by(Task.priority).all()

        return {
            "total_tasks": total_tasks,
            "by_status": dict(status_counts),
            "by_priority": dict(priority_counts)
        }, 200

    @staticmethod
    def search_tasks(user_id, search_term):
        """Searches titles and descriptions using combined filters"""
        if not search_term:
            return {"tasks": []}, 200
            
        search_pattern = f"%{search_term}%"
        tasks = Task.query.filter(
            Task.user_id == user_id,
            Task.is_active == True,
            or_(Task.title.ilike(search_pattern), Task.description.ilike(search_pattern))
        ).all()
        
        return {"tasks": [task.to_dict() for task in tasks]}, 200

    @staticmethod
    def bulk_update_tasks(user_id, data):
        """Updates multiple tasks at once with ownership validation"""
        task_ids = data.get('task_ids', [])
        update_data = data.get('update_data', {})
        
        if not task_ids or not update_data:
            return {"error": True, "message": "Invalid payload format. Provide 'task_ids' and 'update_data'."}, 400

        # Ownership validation: only fetches tasks belonging to this user
        tasks = Task.query.filter(Task.id.in_(task_ids), Task.user_id == user_id, Task.is_active == True).all()
        updated_count = 0
        
        for task in tasks:
            if 'title' in update_data: task.title = update_data['title']
            if 'description' in update_data: task.description = update_data['description']
            if 'status' in update_data: task.status = update_data['status']
            if 'priority' in update_data: task.priority = update_data['priority']
            if 'due_date' in update_data: task.due_date = update_data['due_date']
            
            updated_count += 1
            dynamo_service.log_activity(user_id, "bulk_update", task.id, {"updated_fields": list(update_data.keys())}, TaskService._get_ip())

        db.session.commit()
        return {"message": f"{updated_count} tasks updated successfully"}, 200

    @staticmethod
    def bulk_delete_tasks(user_id, data):
        """Soft deletes multiple tasks at once with ownership validation"""
        task_ids = data.get('task_ids', [])
        if not task_ids:
            return {"error": True, "message": "Invalid payload format. Provide 'task_ids'."}, 400

        tasks = Task.query.filter(Task.id.in_(task_ids), Task.user_id == user_id, Task.is_active == True).all()
        deleted_count = 0
        
        for task in tasks:
            task.is_active = False
            deleted_count += 1
            dynamo_service.log_activity(user_id, "bulk_delete", task.id, {}, TaskService._get_ip())

        db.session.commit()
        return {"message": f"{deleted_count} tasks soft deleted successfully"}, 200