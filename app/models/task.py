import uuid
from datetime import datetime, timezone
from app.extensions import db

class Task(db.Model):
    __tablename__ = 'tasks'

    # Fix 3.4: Consistent UUID strategy
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(150), nullable=False)
    
    # Fix 3.6: Flexible Text field instead of fixed String length
    description = db.Column(db.Text, nullable=True)
    
    status = db.Column(db.String(20), default='todo', nullable=False)
    priority = db.Column(db.String(20), default='medium', nullable=False)
    
    # Foreign key linking to User model
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True) # Required for soft delete
    
    #  Included updated_at
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "user_id": self.user_id,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }