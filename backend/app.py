from flask import Flask
from flask_cors import CORS
from sqlalchemy import text
from models.base import db
from routes.collection_routes import collection_bp
from routes.api_client_routes import api_client_bp
from routes.auth_routes import auth_bp
from routes.workspace_routes import workspace_bp
from routes.request_routes import request_bp
from routes.history_routes import history_bp
from models import collection_model, request_model, user_model, workspace_model, history_model

def create_app():
    app = Flask(__name__)

    app.config[
        'SQLALCHEMY_DATABASE_URI'] = ("mssql+pyodbc://@MSI\\SQLEXPRESS01/"
                                      "API_tester?driver=ODBC+Driver+17+"
                                      "for+SQL+Server")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    CORS(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()
        # Add columns to requests and history tables if they were created before these columns existed
        with db.engine.connect() as conn:
            try:
                conn.execute(text('ALTER TABLE requests ADD auth NVARCHAR(MAX) NULL'))
                conn.commit()
            except Exception:
                pass  # Column already exists
            try:
                conn.execute(text('ALTER TABLE history ADD status INT NULL'))
                conn.commit()
            except Exception:
                pass
            try:
                conn.execute(text('ALTER TABLE history ADD response_time FLOAT NULL'))
                conn.commit()
            except Exception:
                pass
            try:
                conn.execute(text('ALTER TABLE history ADD data NVARCHAR(MAX) NULL'))
                conn.commit()
            except Exception:
                pass

    # Register Blueprints
    app.register_blueprint(api_client_bp)
    app.register_blueprint(collection_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(workspace_bp)
    app.register_blueprint(request_bp)
    app.register_blueprint(history_bp)


    # Simple test route
    @app.route("/")
    def home():
        return {"message": "Backend is running"}
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)