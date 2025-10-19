from flask import Flask


# module imports
from core.database import db
from core.config import Config


# functin to create root instance of the application
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app

app = create_app()

@app.route('/')
def root():
    return {"status":"ok",
            "message":"still alive and running"}, 200



# run the application
if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])