from flask import jsonify


def success(data=None, message="success", code=200):
    """
    On success response
    
    :param data: Data to return
    :param message: Message to return
    :param code: Status code to return
    :return: JSON response
    """
    return jsonify({
        "code": code,
        "msg": message,
        "data": data
    })


def error(message="error", code=400, data=None):
    """
    On error response
    
    :param message: Message to return
    :param code: Status code to return
    :param data: Data to return
    :return: JSON response
    """
    return jsonify({
        "code": code,
        "msg": message,
        "data": data
    })
