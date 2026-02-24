from app import create_app

# Run the app using the development configuration
app = create_app('dev')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)