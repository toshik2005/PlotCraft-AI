"""Helper utility functions."""

from typing import List, Dict, Any
import json


def format_response(success: bool, data: Any = None, message: str = "", errors: List[str] = None) -> Dict[str, Any]:
    """Format API response."""
    response = {
        "success": success,
        "message": message
    }
    
    if data is not None:
        response["data"] = data
    
    if errors:
        response["errors"] = errors
    
    return response


def merge_dicts(*dicts: Dict) -> Dict:
    """Merge multiple dictionaries."""
    result = {}
    for d in dicts:
        result.update(d)
    return result


def safe_json_loads(text: str, default: Any = None) -> Any:
    """Safely parse JSON string."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default
