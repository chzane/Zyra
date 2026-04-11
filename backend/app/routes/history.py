from flask import Blueprint

from app.core.history_store import get_history_store
from app.utils.request_validator import validate_json
from app.utils.response import error, success


history_dp = Blueprint("history", __name__)


@history_dp.route("/records", methods=["GET"])
def historydp_list_records():
    store = get_history_store()

    try:
        return success(data=store.list_records())
    except Exception as exc:
        return error(message=f"List history failed: {exc}", code=500)


@history_dp.route("/records/<hid>", methods=["GET"])
def historydp_get_record(hid: str):
    store = get_history_store()

    try:
        record = store.get_record(hid)
        return success(data=record.to_dict())
    except ValueError as exc:
        return error(message=str(exc), code=404)
    except Exception as exc:
        return error(message=f"Get history failed: {exc}", code=500)


@history_dp.route("/records", methods=["POST"])
@validate_json()
def historydp_create_record(req_json):
    store = get_history_store()

    try:
        record = store.create_record(req_json)
        return success(message="History created", data=record.to_dict())
    except ValueError as exc:
        return error(message=str(exc), code=400)
    except Exception as exc:
        return error(message=f"Create history failed: {exc}", code=500)


@history_dp.route("/records/<hid>", methods=["PUT"])
@validate_json()
def historydp_update_record(hid: str, req_json):
    store = get_history_store()

    try:
        record = store.update_record(hid, req_json)
        return success(message="History updated", data=record.to_dict())
    except ValueError as exc:
        return error(message=str(exc), code=404)
    except Exception as exc:
        return error(message=f"Update history failed: {exc}", code=500)


@history_dp.route("/records/<hid>", methods=["DELETE"])
def historydp_delete_record(hid: str):
    store = get_history_store()

    try:
        record = store.delete_record(hid)
        return success(message="History deleted", data=record.to_dict())
    except ValueError as exc:
        return error(message=str(exc), code=404)
    except Exception as exc:
        return error(message=f"Delete history failed: {exc}", code=500)
