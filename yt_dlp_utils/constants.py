"""Constants."""
from __future__ import annotations

__all__ = ('DEFAULT_RETRY_BACKOFF_FACTOR', 'DEFAULT_RETRY_STATUS_FORCELIST', 'SHARED_HEADERS',
           'USER_AGENT')

DEFAULT_RETRY_STATUS_FORCELIST = (429, 500, 502, 503, 504)
"""Default status codes to retry on."""
DEFAULT_RETRY_BACKOFF_FACTOR = 2.5
"""Default backoff factor for retrying requests."""

USER_AGENT = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/136.0.0.0 Safari/537.36')
"""User agent."""
SHARED_HEADERS = {
    'accept': '*/*',
    'cache-control': 'no-cache',
    'content-type': 'application/vnd.api+json',
    'dnt': '1',
    'pragma': 'no-cache',
    'user-agent': USER_AGENT,
}
"""Default headers for requests."""
