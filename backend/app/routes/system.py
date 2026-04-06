from flask import Blueprint
from app.utils.response import success
from state.state_manager import get_state

system_dp = Blueprint("system", __name__)
state = get_state()


@system_dp.route("/health", methods=["GET"])
def systemdp_health():
    """
    Check system health
    
    :return: JSON response
    :return_code: 200
    :return_msg: "OK"
    :return_data: None
    """
    return success(message="OK")


@system_dp.route("/info", methods=["GET"])
def systemdp_info():
    """
    Get system info
    
    :return: JSON response
    :return_code: 200
    :return_msg: "OK"
    :return_data: System info dictionary
    """
    state.system.refresh()
    return success(data=state.system.to_dict())
