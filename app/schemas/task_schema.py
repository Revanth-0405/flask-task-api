from marshmallow import Schema, fields, validate

class TaskSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=150))
    description = fields.String(load_default=None)
    status = fields.String(validate=validate.OneOf(['todo', 'in_progress', 'done']), load_default='todo')
    priority = fields.String(validate=validate.OneOf(['low', 'medium', 'high']), load_default='medium')
    due_date = fields.DateTime(load_default=None)