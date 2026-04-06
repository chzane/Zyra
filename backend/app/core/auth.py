from pathlib import Path
from state.state_manager import get_state

state = get_state()

def set_token(token: str):
    state.auth.auth_token = token
    if state.state_dir is not None:
        state.save(Path(state.state_dir) / "state.json")

def get_token():
    return state.auth.auth_token
