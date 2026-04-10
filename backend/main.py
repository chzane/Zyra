import sys
from app import create_app
from config import ZyraConfig
from config.config_manager import get_config
from pathlib import Path
from state.state_manager import get_state


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python main.py <token> <port> <is_dev> <app_data_dir>")
        sys.exit(1)

    config: ZyraConfig = get_config()
    state = get_state()
    config.load_env()

    token = sys.argv[1]
    port = int(sys.argv[2])
    is_dev = sys.argv[3] == "true"
    app_data_dir = Path(sys.argv[4])

    config_dir = app_data_dir / "configs"
    state_dir = app_data_dir / "state"

    config_dir.mkdir(parents=True, exist_ok=True)
    state_dir.mkdir(parents=True, exist_ok=True)

    config.config_dir = config_dir
    state.state_dir = state_dir

    config_file = config_dir / "config.json"
    state_file = state_dir / "state.json"
    config.load_or_create(config_file)
    state.load_or_create(state_file)

    config.config_dir = Path(config_dir)
    config.server.port = port
    config.app.is_dev = is_dev
    state.auth.auth_token = token
    state.system.refresh()
    config.save(config_file)
    state.save(state_file)

    app = create_app()

    app.run(host=config.server.host, debug=config.app.is_dev, port=config.server.port)
