from flask import request
from sqlalchemy import or_, func
from app.extensions import db
from app.models.task import Task
from app.services.dynamodb_service import dynamo_service
from datetime import datetime, timedelta, timezone

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
        dynamo_service.log_activity(user_id, "create", new_task.id, {"title": new_task.title}, TaskService._get_ip())
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
    def create_task(data, user_id):
        new_task = Task(
            title=data['title'], description=data.get('description'),
            status=data.get('status', 'todo'), priority=data.get('priority', 'medium'),
            due_date=data.get('due_date'), user_id=user_id
        )
        db.session.add(new_task)
        db.session.commit()
        
        dynamo_service.log_activity(user_id, "create", new_task.id, {"title": new_task.title}, TaskService._get_ip())
        return new_task.to_dict(), 201

    @staticmethod
    def update_task(task_id, user_id, data):
        task = Task.query.filter_by(id=task_id, user_id=user_id, is_active=True).first()
        if not task: return {"error": True, "message": "Not found"}, 404
        
        if 'title' in data: task.title = data['title']
        if 'description' in data: task.description = data['description']
        if 'status' in data: task.status = data['status']
        if 'priority' in data: task.priority = data['priority']
        if 'due_date' in data: task.due_date = data['due_date']
        db.session.commit()
        
        dynamo_service.log_activity(user_id, "update", task.id, data, TaskService._get_ip())
        return task.to_dict(), 200

    @staticmethod
    def delete_task(task_id, user_id):
        task = Task.query.filter_by(id=task_id, user_id=user_id, is_active=True).first()
        if not task: return {"error": True, "message": "Not found"}, 404
        task.is_active = False
        db.session.commit()
        
        dynamo_service.log_activity(user_id, "delete", task.id, {}, TaskService._get_ip())
        return {"message": "Task soft deleted successfully"}, 200

    @staticmethod
    def get_task_stats(user_id):

        now = datetime.now(timezone.utc)
        seven_days_ago = now - timedelta(days=7)
        
        total_tasks = Task.query.filter_by(user_id=user_id, is_active=True).count()
        status_counts = db.session.query(Task.status, func.count(Task.id)).filter_by(user_id=user_id, is_active=True).group_by(Task.status).all()
        priority_counts = db.session.query(Task.priority, func.count(Task.id)).filter_by(user_id=user_id, is_active=True).group_by(Task.priority).all()

        overdue_count = Task.query.filter(Task.user_id == user_id, Task.is_active == True, Task.due_date < now.date(), Task.status != 'done').count()
        completed_this_week = Task.query.filter(Task.user_id == user_id, Task.is_active == True, Task.status == 'done', Task.updated_at >= seven_days_ago).count()

        completed_tasks = Task.query.filter_by(user_id=user_id, is_active=True, status='done').all()
        avg_completion_time_hours = 0
        if completed_tasks:
            total_seconds = sum((t.updated_at - t.created_at).total_seconds() for t in completed_tasks if t.updated_at and t.created_at)
            avg_completion_time_hours = round((total_seconds / len(completed_tasks)) / 3600, 2)

        return {
            "total_tasks": total_tasks,
            "by_status": dict(status_counts),
            "by_priority": dict(priority_counts),
            "overdue_count": overdue_count,
            "completed_this_week": completed_this_week,
            "avg_completion_time_hours": avg_completion_time_hours
        }, 200

    @staticmethod
    def search_tasks(user_id, search_term, status=None, priority=None, date_from=None, date_to=None):
        """Searches titles and descriptions using combined filters (Fixes 6.6)"""
        query = Task.query.filter(Task.user_id == user_id, Task.is_active == True)

        # Text Search (ILIKE)
        if search_term:
            search_pattern = f"%{search_term}%"
            query = query.filter(or_(Task.title.ilike(search_pattern), Task.description.ilike(search_pattern)))
        
        # Combined Filters
        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == priority)
        if date_from:
            query = query.filter(Task.due_date >= date_from)
        if date_to:
            query = query.filter(Task.due_date <= date_to)

        tasks = query.all()
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