from functools import wraps
from flask import session, jsonify, current_app, make_response
from datetime import datetime, timedelta

def check_session_timeout():
    """
    Middleware function to check session timeout.
    Should be registered as a @before_app_request function.
    """
    current_app.permanent_session_lifetime = timedelta(minutes=30)  # Session timeout set to 30 minutes

    last_activity = session.get('last_activity')
    if last_activity:
        # Check if the session has timed out
        if datetime.utcnow() > datetime.fromisoformat(last_activity) + timedelta(minutes=30):
            session.clear()  # Clear the session

            # Create a response object to clear cookies
            response = make_response(jsonify({"message": "Session expired, please log in again."}), 403)
            response.delete_cookie('session')  # Delete the session cookie
            response.delete_cookie('csrf_token', path='/')  # If using CSRF tokens stored in cookies
            # Add any additional cookies to clear as needed
            
            return response

    # Update the last activity timestamp
    session['last_activity'] = datetime.utcnow().isoformat()


def session_required(f):
    """
    Decorator to ensure the user is logged in with an active session.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return jsonify({
                "message": "Session is missing or invalid!",
                "notification": "Please log in to access this resource."
            }), 403
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorator to ensure the user has admin privileges.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the user is logged in by verifying session data
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                "message": "Unauthorized access!",
                "notification": "You must be logged in to perform this action."
            }), 403

        # Fetch the user from the database
        from models.dbSchema import User  # Ensure you import your database schema
        user = User.query.filter_by(id=user_id).first()

        # Check if the user exists and has admin privileges
        if not user or not getattr(user, 'is_admin', False):
            return jsonify({
                "message": "Access denied!",
                "notification": "You do not have sufficient privileges."
            }), 403

        # Allow access to the route
        return f(*args, **kwargs)
    return decorated_function
