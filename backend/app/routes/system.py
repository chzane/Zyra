from flask import Blueprint, jsonify
from app.utils.response import success, error
from app.core.system import zyra_system_info

system_dp = Blueprint("system", __name__)


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
    return success(data=zyra_system_info.to_dict())
