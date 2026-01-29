"""Async utilities."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
import asyncio
import logging
import sys

from aiohttp_retry import ExponentialRetry, RetryClient
from typing_extensions import Self, Unpack
from yt_dlp.cookies import extract_cookies_from_browser
import aiohttp
import yt_dlp

from .constants import DEFAULT_RETRY_BACKOFF_FACTOR, DEFAULT_RETRY_STATUS_FORCELIST, SHARED_HEADERS
from .lib import YoutubeDLLogger

if TYPE_CHECKING:
    from collections.abc import Collection, Iterable, Mapping

__all__ = ('AsyncYoutubeDL', 'get_configured_yt_dlp', 'setup_session')

log = logging.getLogger(__name__)


class AsyncYoutubeDL:
    """
    Async wrapper around ``yt_dlp.YoutubeDL``.

    This class wraps a synchronous ``YoutubeDL`` instance and provides async methods
    that run blocking operations in a thread executor.

    Only ``download`` and ``extract_info`` are implemented in this wrapper.

    Parameters
    ----------
    ydl : yt_dlp.YoutubeDL
        The wrapped ``YoutubeDL`` instance.
    """
    def __init__(self, ydl: yt_dlp.YoutubeDL) -> None:
        self.ydl = ydl
        """The wrapped ``YoutubeDL`` instance."""

    async def extract_info(self,
                           url: str,
                           ie_key: str | None = None,
                           extra_info: Mapping[str, Any] | None = None,
                           *,
                           download: bool = True,
                           process: bool = True,
                           force_generic_extractor: bool = False) -> dict[str, Any] | None:
        """Extract info asynchronously.

        Parameters
        ----------
        url : str
            The URL to extract info from.
        download : bool
            Whether to download the video. Default is True.
        ie_key : str | None
            The extractor key to use.
        extra_info : Mapping[str, Any] | None
            Extra info to pass to the extractor.
        process : bool
            Whether to process the info. Default is True.
        force_generic_extractor : bool
            Whether to force the generic extractor. Default is False.

        Returns
        -------
        dict[str, Any] | None
            The extracted info, or None if extraction failed.
        """
        extra_info = dict(extra_info) if extra_info else {}
        result = await asyncio.to_thread(self.ydl.extract_info,
                                         url,
                                         download=download,
                                         ie_key=ie_key,
                                         extra_info=extra_info,
                                         process=process,
                                         force_generic_extractor=force_generic_extractor)
        return dict(result) if result is not None else None

    async def download(self, urls: Iterable[str]) -> int:
        """Download videos asynchronously.

        Parameters
        ----------
        urls : Iterable[str]
            The URLs to download.

        Returns
        -------
        int
            The return code (0 for success).
        """
        return cast('int', await asyncio.to_thread(self.ydl.download, list(urls)))

    async def __aenter__(self) -> Self:
        """Enter the async context manager."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Exit the async context manager."""
        self.ydl.__exit__(*args)


def get_configured_yt_dlp(sleep_time: int = 3,
                          *,
                          debug: bool = False,
                          **kwargs: Unpack[yt_dlp._Params]) -> AsyncYoutubeDL:
    """
    Get an async-wrapped configured ``YoutubeDL`` instance.

    This function sets up a ``yt_dlp.YoutubeDL`` instance with the user's configuration (e.g.
    located at ``~/.config/yt-dlp/config``). It overrides the default logger (``logger`` option),
    disables colours (``color`` option), and sets the sleep time between requests
    (``sleep_interval_requests`` option). It also sets the ``verbose`` flag based on the ``debug``
    parameter.

    All other keyword arguments are passed directly to the ``yt_dlp.YoutubeDL`` constructor.

    Parameters
    ----------
    sleep_time : int
        The time to sleep between requests, in seconds. Default is 3 seconds.
    debug : bool
        Whether to enable debug mode. Default is False.

    Returns
    -------
    AsyncYoutubeDL
        An async wrapper around a configured ``yt_dlp.YoutubeDL`` instance.
    """
    old_sys_argv = sys.argv
    sys.argv = [sys.argv[0]]
    ydl_opts = yt_dlp.parse_options()[-1]
    ydl_opts['color'] = {'stdout': 'never', 'stderr': 'never'}
    ydl_opts['logger'] = kwargs.pop('logger', YoutubeDLLogger())
    ydl_opts['sleep_interval_requests'] = sleep_time
    ydl_opts['verbose'] = debug
    sys.argv = old_sys_argv
    return AsyncYoutubeDL(yt_dlp.YoutubeDL(ydl_opts | kwargs))


async def setup_session(browser: str,
                        profile: str,
                        add_headers: Mapping[str, str] | None = None,
                        backoff_factor: float = DEFAULT_RETRY_BACKOFF_FACTOR,
                        domains: Iterable[str] | None = None,
                        headers: Mapping[str, str] | None = None,
                        session: aiohttp.ClientSession | None = None,
                        status_forcelist: Collection[int] = DEFAULT_RETRY_STATUS_FORCELIST,
                        *,
                        setup_retry: bool = False) -> aiohttp.ClientSession | RetryClient:
    """
    Create or modify an aiohttp :py:class:`aiohttp.ClientSession` with cookies from the browser.

    Parameters
    ----------
    browser : str
        The browser to extract cookies from.
    profile : str
        The profile to extract cookies from.
    add_headers : Mapping[str, str]
        Additional headers to add to the session.
    backoff_factor : float
        The backoff factor to use for the retry mechanism.
    domains : Iterable[str]
        Filter the cookies to only those that match the specified domains.
    headers : Mapping[str, str]
        The headers to use for the session. If not specified, a default set will be used.
    session : aiohttp.ClientSession | None
        An existing session to modify. If not specified, a new session will be created.
    status_forcelist : Collection[int]
        The status codes to retry on.
    setup_retry : bool
        Whether to set up a retry mechanism for the session.

    Returns
    -------
    aiohttp.ClientSession | RetryClient
        An aiohttp session, or a RetryClient if ``setup_retry`` is True.

    Notes
    -----
    The session should be used as an async context manager or closed explicitly when done.
    """
    final_headers = dict(headers or SHARED_HEADERS)
    if add_headers:
        final_headers.update(add_headers)
    extracted = await asyncio.to_thread(extract_cookies_from_browser, browser, profile)
    cookies: dict[str, str] = {}
    if not domains:
        for cookie in extracted:
            if isinstance(cookie.value, str):
                cookies[cookie.name] = cookie.value
    else:
        for domain in (d.lstrip('.') for d in domains):
            for cookie in extracted.get_cookies_for_url(f'https://{domain}'):
                if isinstance(cookie.value, str):
                    cookies[cookie.name] = cookie.value
    if session is None:
        session = aiohttp.ClientSession(headers=final_headers, cookies=cookies)
    else:
        session.headers.update(final_headers)
        session.cookie_jar.update_cookies(cookies)
    if setup_retry:
        return RetryClient(client_session=session,
                           retry_options=ExponentialRetry(statuses=set(status_forcelist),
                                                          factor=backoff_factor))
    return session
