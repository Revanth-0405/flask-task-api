import os
from app import create_app

# Run the app using the development configuration
env = os.getenv('FLASK_ENV', 'dev')
app = create_app(env)

if __name__ == '__main__':
    app.run(debug=True if env == 'development' else False)