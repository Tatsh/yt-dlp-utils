from __future__ import annotations

from typing import TYPE_CHECKING

from aiohttp_retry import RetryClient
from yarl import URL
from yt_dlp_utils.aio import AsyncYoutubeDL, get_configured_yt_dlp, setup_session
from yt_dlp_utils.constants import SHARED_HEADERS
import aiohttp
import pytest
import yt_dlp.cookies

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.mark.asyncio
async def test_setup_session_no_domains(mocker: MockerFixture) -> None:
    cookie = mocker.Mock(value='value1')
    cookie.name = 'cookie1'
    mock_jar = mocker.Mock(spec=yt_dlp.cookies.YoutubeDLCookieJar)
    mock_jar.__iter__ = mocker.Mock(return_value=iter([cookie]))
    mocker.patch('yt_dlp_utils.aio.extract_cookies_from_browser', return_value=mock_jar)

    session = await setup_session(browser='chrome', profile='default')

    try:
        assert isinstance(session, aiohttp.ClientSession)
        assert session.headers['user-agent'] == SHARED_HEADERS['user-agent']
        assert 'cookie1' in session.cookie_jar.filter_cookies(URL('https://example.com'))
    finally:
        await session.close()


@pytest.mark.asyncio
async def test_setup_session_with_domains(mocker: MockerFixture) -> None:
    cookie1 = mocker.Mock(value='value1', domain='example.com')
    cookie1.name = 'cookie1'
    mock_jar = mocker.Mock(spec=yt_dlp.cookies.YoutubeDLCookieJar)
    mock_jar.get_cookies_for_url.return_value = [cookie1]
    mocker.patch('yt_dlp_utils.aio.extract_cookies_from_browser', return_value=mock_jar)

    session = await setup_session(browser='chrome', profile='default', domains=['example.com'])

    try:
        assert isinstance(session, aiohttp.ClientSession)
        mock_jar.get_cookies_for_url.assert_called_once_with('https://example.com')
        assert session.headers['user-agent'] == SHARED_HEADERS['user-agent']
    finally:
        await session.close()


@pytest.mark.asyncio
async def test_setup_session_no_domains_non_string_cookie(mocker: MockerFixture) -> None:
    cookie_str = mocker.Mock(value='value1')
    cookie_str.name = 'cookie1'
    cookie_int = mocker.Mock(value=123)
    cookie_int.name = 'cookie2'
    mock_jar = mocker.Mock(spec=yt_dlp.cookies.YoutubeDLCookieJar)
    mock_jar.__iter__ = mocker.Mock(return_value=iter([cookie_str, cookie_int]))
    mocker.patch('yt_dlp_utils.aio.extract_cookies_from_browser', return_value=mock_jar)

    session = await setup_session(browser='chrome', profile='default')

    try:
        assert isinstance(session, aiohttp.ClientSession)
        cookies = session.cookie_jar.filter_cookies(URL('https://example.com'))
        assert 'cookie1' in cookies
        assert 'cookie2' not in cookies
    finally:
        await session.close()


@pytest.mark.asyncio
async def test_setup_session_with_domains_non_string_cookie(mocker: MockerFixture) -> None:
    cookie_str = mocker.Mock(value='value1', domain='example.com')
    cookie_str.name = 'cookie1'
    cookie_int = mocker.Mock(value=456, domain='example.com')
    cookie_int.name = 'cookie2'
    mock_jar = mocker.Mock(spec=yt_dlp.cookies.YoutubeDLCookieJar)
    mock_jar.get_cookies_for_url.return_value = [cookie_str, cookie_int]
    mocker.patch('yt_dlp_utils.aio.extract_cookies_from_browser', return_value=mock_jar)

    session = await setup_session(browser='chrome', profile='default', domains=['example.com'])

    try:
        assert isinstance(session, aiohttp.ClientSession)
        cookies = session.cookie_jar.filter_cookies(URL('https://example.com'))
        assert 'cookie1' in cookies
        assert 'cookie2' not in cookies
    finally:
        await session.close()


@pytest.mark.asyncio
async def test_setup_session_with_custom_headers(mocker: MockerFixture) -> None:
    mock_jar = mocker.Mock(spec=yt_dlp.cookies.YoutubeDLCookieJar)
    mock_jar.__iter__ = mocker.Mock(return_value=iter([]))
    mocker.patch('yt_dlp_utils.aio.extract_cookies_from_browser', return_value=mock_jar)

    session = await setup_session(browser='chrome',
                                  profile='default',
                                  headers={'Custom-Header': 'CustomValue'},
                                  add_headers={'Another-Header': 'AnotherValue'})

    try:
        assert isinstance(session, aiohttp.ClientSession)
        assert session.headers['Custom-Header'] == 'CustomValue'
        assert session.headers['Another-Header'] == 'AnotherValue'
    finally:
        await session.close()


@pytest.mark.asyncio
async def test_setup_session_with_existing_session(mocker: MockerFixture) -> None:
    mock_jar = mocker.Mock(spec=yt_dlp.cookies.YoutubeDLCookieJar)
    mock_jar.__iter__ = mocker.Mock(return_value=iter([]))
    mocker.patch('yt_dlp_utils.aio.extract_cookies_from_browser', return_value=mock_jar)

    existing_session = aiohttp.ClientSession()
    try:
        session = await setup_session(browser='chrome', profile='default', session=existing_session)
        assert isinstance(session, aiohttp.ClientSession)
        assert session is existing_session
        assert session.headers['user-agent'] == SHARED_HEADERS['user-agent']
    finally:
        await existing_session.close()


def test_get_configured_yt_dlp_default(mocker: MockerFixture) -> None:
    mocker.patch('yt_dlp.parse_options', return_value=({}, {}, {}))
    mock_yt_dlp = mocker.patch('yt_dlp.YoutubeDL')

    result = get_configured_yt_dlp()

    assert isinstance(result, AsyncYoutubeDL)
    mock_yt_dlp.assert_called_once_with({
        'color': {
            'stdout': 'never',
            'stderr': 'never'
        },
        'logger': mocker.ANY,
        'sleep_interval_requests': 3,
        'verbose': False
    })


def test_get_configured_yt_dlp_with_custom_params(mocker: MockerFixture) -> None:
    mocker.patch('yt_dlp.parse_options', return_value=({}, {}, {}))
    mock_yt_dlp = mocker.patch('yt_dlp.YoutubeDL')

    result = get_configured_yt_dlp(sleep_time=5,
                                   debug=True,
                                   http_headers={'referer': 'https://example.com'})

    assert isinstance(result, AsyncYoutubeDL)
    mock_yt_dlp.assert_called_once_with({
        'color': {
            'stdout': 'never',
            'stderr': 'never'
        },
        'http_headers': {
            'referer': 'https://example.com'
        },
        'logger': mocker.ANY,
        'sleep_interval_requests': 5,
        'verbose': True
    })


@pytest.mark.asyncio
async def test_async_youtube_dl_extract_info(mocker: MockerFixture) -> None:
    mock_ydl = mocker.Mock(spec=yt_dlp.YoutubeDL)
    mock_ydl.extract_info.return_value = {'id': 'test123', 'title': 'Test Video'}

    async_ydl = AsyncYoutubeDL(mock_ydl)
    result = await async_ydl.extract_info('https://example.com/video', download=False)

    assert result == {'id': 'test123', 'title': 'Test Video'}
    mock_ydl.extract_info.assert_called_once_with('https://example.com/video',
                                                  download=False,
                                                  ie_key=None,
                                                  extra_info={},
                                                  process=True,
                                                  force_generic_extractor=False)


@pytest.mark.asyncio
async def test_async_youtube_dl_download(mocker: MockerFixture) -> None:
    mock_ydl = mocker.Mock(spec=yt_dlp.YoutubeDL)
    mock_ydl.download.return_value = 0

    async_ydl = AsyncYoutubeDL(mock_ydl)
    result = await async_ydl.download(['https://example.com/video1', 'https://example.com/video2'])

    assert result == 0
    mock_ydl.download.assert_called_once_with(
        ['https://example.com/video1', 'https://example.com/video2'])


@pytest.mark.asyncio
async def test_async_youtube_dl_context_manager(mocker: MockerFixture) -> None:
    mock_ydl = mocker.Mock(spec=yt_dlp.YoutubeDL)
    mock_ydl.__exit__ = mocker.Mock()

    async with AsyncYoutubeDL(mock_ydl) as async_ydl:
        assert async_ydl.ydl is mock_ydl

    mock_ydl.__exit__.assert_called_once()


def test_async_youtube_dl_ydl_property(mocker: MockerFixture) -> None:
    mock_ydl = mocker.Mock(spec=yt_dlp.YoutubeDL)
    async_ydl = AsyncYoutubeDL(mock_ydl)

    assert async_ydl.ydl is mock_ydl


@pytest.mark.asyncio
async def test_setup_session_with_retry(mocker: MockerFixture) -> None:
    mock_jar = mocker.Mock(spec=yt_dlp.cookies.YoutubeDLCookieJar)
    mock_jar.__iter__ = mocker.Mock(return_value=iter([]))
    mocker.patch('yt_dlp_utils.aio.extract_cookies_from_browser', return_value=mock_jar)

    client = await setup_session(browser='chrome',
                                 profile='default',
                                 setup_retry=True,
                                 backoff_factor=0.5,
                                 status_forcelist=[500, 502, 503])

    try:
        assert isinstance(client, RetryClient)
    finally:
        await client.close()
