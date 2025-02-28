from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask import Flask, jsonify, render_template
from werkzeug.exceptions import NotFound
from flask_bcrypt import Bcrypt

from models.dbSchema import db

# Import blueprints from respective modules
from apis.routes.auth_login import auth_bp, oauth_bp
from apis.routes.search import search_bp
from apis.routes.user import  user_bp, users            ## users -> gets users.. user_bp -> adds a user


bcrypt = Bcrypt()  # Initialize Bcrypt


def create_app():

    app = Flask(__name__, static_folder='static', template_folder='templates')
    CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}})
    # Load configuration
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = 'your_secret_key'

    # Initialize extensions
    db.init_app(app)
    oauth = OAuth(app)

    # blueprints
    app.register_blueprint(auth_bp,         url_prefix= '/auth')
    app.register_blueprint(search_bp,       url_prefix='/search')
    app.register_blueprint(oauth_bp,        url_prefix= '/oauth')
    app.register_blueprint(user_bp,         url_prefix= '/users')
    app.register_blueprint(users,           url_prefix= '/users')

    ##fefa    
    


    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "API Gateway is running"}), 200

    @app.route('/')
    def index():
        return render_template('index.html')

    # Error handler for invalid routes
    @app.errorhandler(NotFound)
    def handle_not_found(error):
        return jsonify({"error": "Endpoint not found"}), 404

    return app


# Create and configure the Flask app instance
app = create_app()

# Ensure database tables are created
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    CORS(app)
