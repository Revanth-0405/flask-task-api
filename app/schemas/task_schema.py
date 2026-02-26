from marshmallow import Schema, fields, validate

class TaskSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=150))
    description = fields.String(missing=None)
    status = fields.String(validate=validate.OneOf(['todo', 'in_progress', 'done']), missing='todo')
    priority = fields.String(validate=validate.OneOf(['low', 'medium', 'high']), missing='medium')
    due_date = fields.DateTime(missing=None)