from flask import jsonify
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({
            "error": True,
            "message": "Bad Request",
            "details": str(e.description)
        }), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({
            "error": True,
            "message": "Unauthorized",
            "details": str(e.description)
        }), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({
            "error": True,
            "message": "Forbidden",
            "details": str(e.description)
        }), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "error": True,
            "message": "Resource Not Found",
            "details": str(e.description)
        }), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({
            "error": True,
            "message": "Internal Server Error",
            "details": "An unexpected error occurred on the server."
        }), 500

    # Catch-all for any other standard HTTP errors
    @app.errorhandler(HTTPException)
    def handle_exception(e):
        return jsonify({
            "error": True,
            "message": e.name,
            "details": e.description
        }), e.code
        
    # Catch-all for unhandled generic Python exceptions
    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        return jsonify({
            "error": True,
            "message": "Internal Server Error",
            "details": str(e) # In production, you might want to hide the exact error string
        }), 500