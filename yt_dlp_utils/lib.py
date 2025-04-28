"""Utilities."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any
import logging
import re
import sys

from requests.adapters import HTTPAdapter
from urllib3 import Retry
from yt_dlp.cookies import extract_cookies_from_browser
import requests
import yt_dlp

from .constants import DEFAULT_RETRY_BACKOFF_FACTOR, DEFAULT_RETRY_STATUS_FORCELIST, SHARED_HEADERS

if TYPE_CHECKING:
    from collections.abc import Collection, Iterable, Mapping

__all__ = ('YoutubeDLLogger', 'get_configured_yt_dlp', 'setup_session')

log = logging.getLogger(__name__)


class YoutubeDLLogger(yt_dlp.cookies.YDLLogger):
    """Logger for yt-dlp."""
    def debug(self, message: str) -> None:
        """Log a debug message."""
        if re.match(r'^\[download\]\s+[0-9\.]+%', message):
            return
        log.info('%s', re.sub(r'^\[(?:info|debug)\]\s+', '', message))

    def info(self, message: str) -> None:
        """Log an info message."""
        log.info('%s', re.sub(r'^\[info\]\s+', '', message))

    def warning(
            self,
            message: str,
            once: bool = False,  # noqa: FBT001, FBT002
            only_once: bool = False) -> None:  # noqa: FBT001, FBT002
        """Log a warning message."""
        log.warning('%s', re.sub(r'^\[warn(?:ing)?\]\s+', '', message))

    def error(self, message: str) -> None:
        """Log an error message."""
        log.error('%s', re.sub(r'^\[err(?:or)?\]\s+', '', message))


def get_configured_yt_dlp(sleep_time: int = 3,
                          logger: Any = None,
                          *,
                          debug: bool = False) -> yt_dlp.YoutubeDL:
    """
    Get a configured ``YoutubeDL`` instance.

    This function sets up a ``yt_dlp.YoutubeDL`` instance with the user's configuration (e.g.
    located at ``~/.config/yt-dlp/config``). It overrides the default logger, disables colours, and
    sets the sleep time between requests. It also sets the verbose flag based on the ``debug``
    parameter.

    Parameters
    ----------
    sleep_time : int
        The time to sleep between requests, in seconds. Default is 3 seconds.
    logger : Any
        The logger to use. See :py:class:`YoutubeDLLogger` for details.
    debug : bool
        Whether to enable debug mode. Default is False.

    Returns
    -------
    yt_dlp.YoutubeDL
        A configured instance of `yt_dlp.YoutubeDL`_.
    """
    old_sys_argv = sys.argv
    sys.argv = [sys.argv[0]]
    ydl_opts = yt_dlp.parse_options()[-1]
    ydl_opts['color'] = {'stdout': 'never', 'stderr': 'never'}
    ydl_opts['logger'] = logger or YoutubeDLLogger()
    ydl_opts['sleep_interval_requests'] = sleep_time
    ydl_opts['verbose'] = debug
    sys.argv = old_sys_argv
    return yt_dlp.YoutubeDL(ydl_opts)


def setup_session(browser: str,
                  profile: str,
                  add_headers: Mapping[str, str] | None = None,
                  backoff_factor: float = DEFAULT_RETRY_BACKOFF_FACTOR,
                  domains: Iterable[str] | None = None,
                  headers: Mapping[str, str] | None = None,
                  session: requests.Session | None = None,
                  status_forcelist: Collection[int] = DEFAULT_RETRY_STATUS_FORCELIST,
                  *,
                  setup_retry: bool = False) -> requests.Session:
    """
    Create or modify a Requests :py:class:`requests.Session` instance with cookies from the browser.

    Parameters
    ----------
    browser : str
        The browser to extract cookies from.
    profile : str
        The profile to extract cookies from.
    add_headers : Mapping[str, str]
        Additional headers to add to the requests session.
    backoff_factor : float
        The backoff factor to use for the retry mechanism.
    domains : Iterable[str]
        Filter the cookies to only those that match the specified domains.
    headers : Mapping[str, str]
        The headers to use for the requests session. If not specified, a default set will be used.
    status_forcelist : Collection[int]
        The status codes to retry on.
    setup_retry : bool
        Whether to set up a retry mechanism for the Requests session.

    Returns
    -------
    requests.Session
        A Requests session.
    """
    headers = headers or SHARED_HEADERS
    add_headers = add_headers or {}
    session = session or requests.Session()
    session.headers.update(headers)
    session.headers.update(add_headers)
    if setup_retry:
        session.mount(
            'https://',
            HTTPAdapter(max_retries=Retry(backoff_factor=backoff_factor,
                                          status_forcelist=status_forcelist)))
    extracted = extract_cookies_from_browser(browser, profile)
    if not domains:
        session.cookies.update(extracted)
    else:
        for domain in (d.lstrip('.') for d in domains):
            for cookie in extracted.get_cookies_for_url(f'https://{domain}'):
                if not isinstance(cookie.value, str):
                    continue
                session.cookies.set(cookie.name, cookie.value, domain=domain)
    return session
