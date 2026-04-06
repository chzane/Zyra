def _usage_to_dict(usage):
    """
    Convert usage object to dictionary
    
    :param usage: Usage object
    :return: Dictionary of usage metrics
    """
    if not usage:
        return None
    return {
        "completion_tokens": getattr(usage, "completion_tokens", None),
        "prompt_cache_hit_tokens": getattr(usage, "prompt_cache_hit_tokens", None),
        "prompt_cache_miss_tokens": getattr(usage, "prompt_cache_miss_tokens", None),
        "prompt_tokens": getattr(usage, "prompt_tokens", None),
        "total_tokens": getattr(usage, "total_tokens", None)
    }


def _api_data_from_response(resp, choices):
    """
    Convert response object to dictionary
    
    :param resp: Response object
    :param choices: List of choices
    :return: Dictionary of response data
    """
    return {
        "id": resp.id,
        "object": resp.object,
        "model": resp.model,
        "choices": choices,
        "usage": _usage_to_dict(resp.usage),
    }


def _default_choice_message():
    return {
        "annotations": None,
        "audio": None,
        "content": None,
        "function_call": None,
        "reasoning_content": None,
        "refusal": None,
        "role": "assistant",
        "tool_calls": None,
    }


def _merge_stream_value(base_value, incoming_value, key=None):
    """
    Merge stream values, handling strings, dictionaries, and lists.
    
    :param base_value: Base value to merge into
    :param incoming_value: Value to merge from
    :param key: Optional key to use for string concatenation
    :return: Merged value
    """
    if incoming_value is None:
        return base_value
    if base_value is None:
        return incoming_value

    append_keys = {"content", "reasoning_content", "arguments"}
    if isinstance(base_value, str) and isinstance(incoming_value, str):
        if key in append_keys:
            return base_value + incoming_value
        return incoming_value

    if isinstance(base_value, dict) and isinstance(incoming_value, dict):
        merged = dict(base_value)
        for child_key, child_value in incoming_value.items():
            merged[child_key] = _merge_stream_value(merged.get(child_key), child_value, child_key)
        return merged

    if isinstance(base_value, list) and isinstance(incoming_value, list):
        merged = list(base_value)
        for index, item in enumerate(incoming_value):
            if index < len(merged):
                merged[index] = _merge_stream_value(merged[index], item, key)
            else:
                merged.append(item)
        return merged

    return incoming_value


def _normalize_choice_message(choice_message):
    normalized = _default_choice_message()
    normalized.update(choice_message)
    return normalized