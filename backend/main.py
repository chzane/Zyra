import sys
from app import create_app
from app.core.auth import set_token

app = create_app()

if __name__ == "__main__":
    token = sys.argv[1] if len(sys.argv) > 1 else None
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    is_dev = sys.argv[3] == "true" if len(sys.argv) > 3 else False
    
    set_token(token)
    
    app.run(host="127.0.0.1", debug=is_dev, port=port)
