import sys
from app import create_app
from app.core.auth import set_token

app = create_app()

if __name__ == "__main__":
    token = sys.argv[1] if len(sys.argv) > 1 else None
    set_token(token)
    
    app.run(debug=True)