# Main Flask application entry point and mock routes
from test_codebase import database, auth

def handle_home_route() -> str:
    """
    Simulates loading the home page of the application.
    Returns a simple welcome text.
    """
    return "Welcome to the Mock Flask App home page!"

def handle_register_route(request_data: dict) -> dict:
    """
    Simulates handling POST request to register a new user account.
    Examines incoming username and password fields.
    """
    username = request_data.get("username")
    password = request_data.get("password")
    
    if not username or not password:
        return {"status": "error", "message": "Missing username or password"}
        
    success = auth.register_user(username, password)
    if success:
        return {"status": "success", "message": "User registered successfully"}
    return {"status": "error", "message": "Username already exists"}

def handle_login_route(request_data: dict) -> dict:
    """
    Simulates handling POST request to validate login credentials.
    Returns user details upon successful validation.
    """
    username = request_data.get("username")
    password = request_data.get("password")
    
    user = auth.verify_login(username, password)
    if user:
        return {"status": "success", "user": user.to_dict()}
    return {"status": "error", "message": "Invalid username or password"}

def start_server():
    """
    Bootstraps database tables and starts the server loop.
    """
    print("Starting system engine...")
    database.initialize_database()
    print("Mock server is running.")
