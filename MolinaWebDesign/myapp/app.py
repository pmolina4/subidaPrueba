from flask import Flask
from models import init_db
from views import init_views

def create_app():
    app = Flask(__name__)
    app.secret_key = "abcd1234"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///persianas_molina.sqlite3"

    with app.app_context():
        db_access = init_db(app)
        init_views(app, db_access)

    return app

app = create_app()

if __name__ == "__main__":
    app.run( host="0.0.0.0", port=5000,  debug=True)
