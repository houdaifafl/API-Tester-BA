from flask import Flask
from sqlalchemy import create_engine
from backend.models.base import db
from backend.routes.collection_routes import collection_bp
from routes.api_client_routes import api_client_bp
from backend.models import collection_model, request_model

def create_app():
    app = Flask(__name__)

    app.config[
        'SQLALCHEMY_DATABASE_URI'] = ("mssql+pyodbc://@MSI\\SQLEXPRESS01/"
                                      "API_tester?driver=ODBC+Driver+17+"
                                      "for+SQL+Server")
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Register Blueprints
    app.register_blueprint(api_client_bp)
    app.register_blueprint(collection_bp)

    # Simple test route
    @app.route("/")
    def home():
        return {"message": "Backend is running"}
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)