import requests
from utils.text import handle_request_error


def api_request(method: str, url: str, action: str, **kwargs):
    """Perform an HTTP request, surfacing a UI error and returning None if it
    fails; otherwise returns the successful `requests.Response`."""
    try:
        response = getattr(requests, method)(url, **kwargs)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        handle_request_error(action, e)
        return None
