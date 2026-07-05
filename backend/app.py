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
from routes.invitation_routes import invitation_bp
from routes.admin_routes import admin_bp
from models import collection_model, request_model, user_model, workspace_model, history_model, workspace_member_model, invitation_model, audit_log_model, notification_model

def safe_add_column(conn, table, column, col_type, logger):
    try:
        conn.execute(text(f"ALTER TABLE {table} ADD {column} {col_type} NULL"))
        conn.commit()
    except Exception as e:
        err_str = str(e).lower()
        if "2705" in err_str or "42s21" in err_str or "duplicate" in err_str or "already exists" in err_str:
            pass  # Column already exists, safe to ignore
        else:
            logger.warning(f"Database migration error adding column '{column}' to '{table}': {e}")

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
            # Purge legacy invitations
            try:
                conn.execute(text("DELETE FROM invitations"))
                conn.commit()
            except Exception as e:
                app.logger.warning(f"Error purging legacy invitations: {e}")

            safe_add_column(conn, 'requests', 'auth', 'NVARCHAR(MAX)', app.logger)
            safe_add_column(conn, 'history', 'status', 'INT', app.logger)
            safe_add_column(conn, 'history', 'response_time', 'FLOAT', app.logger)
            safe_add_column(conn, 'history', 'data', 'NVARCHAR(MAX)', app.logger)
            safe_add_column(conn, 'invitations', 'role', 'VARCHAR(20)', app.logger)
            safe_add_column(conn, 'workspace_members', 'role', 'VARCHAR(20)', app.logger)

            is_sqlite = 'sqlite' in str(db.engine.url)
            bool_col_type = 'BOOLEAN' if is_sqlite else 'BIT'
            safe_add_column(conn, 'users', 'is_admin', bool_col_type, app.logger)
            safe_add_column(conn, 'users', 'is_suspended', bool_col_type, app.logger)

            # Backfill existing NULL roles
            try:
                conn.execute(text("UPDATE workspace_members SET role = 'viewer' WHERE role IS NULL"))
                conn.execute(text("UPDATE invitations SET role = 'viewer' WHERE role IS NULL"))
                conn.execute(text("UPDATE users SET is_admin = 0 WHERE is_admin IS NULL"))
                conn.execute(text("UPDATE users SET is_suspended = 0 WHERE is_suspended IS NULL"))
                conn.commit()
            except Exception as e:
                app.logger.warning(f"Error backfilling roles and admin: {e}")

            # Clean up workspaces owned by admin accounts
            try:
                from models.user_model import User
                from models.workspace_model import Workspace
                admins = User.query.filter_by(is_admin=True).all()
                for admin in admins:
                    for ws in list(admin.workspaces):
                        db.session.delete(ws)
                db.session.commit()
            except Exception as e:
                app.logger.warning(f"Error cleaning up admin workspaces on startup: {e}")

    # Register Blueprints
    app.register_blueprint(api_client_bp)
    app.register_blueprint(collection_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(workspace_bp)
    app.register_blueprint(request_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(invitation_bp)
    app.register_blueprint(admin_bp)


    # Simple test route
    @app.route("/")
    def home():
        return {"message": "Backend is running"}
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)