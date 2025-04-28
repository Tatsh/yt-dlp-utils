from __future__ import annotations

from typing import TYPE_CHECKING, cast

from yt_dlp_utils.constants import SHARED_HEADERS
from yt_dlp_utils.lib import YoutubeDLLogger, get_configured_yt_dlp, setup_session
import yt_dlp
import yt_dlp.cookies

if TYPE_CHECKING:
    from unittest.mock import Mock

    from pytest_mock import MockerFixture


def test_youtube_dl_logger(mocker: MockerFixture) -> None:
    logger = YoutubeDLLogger()
    mock_log_info = mocker.patch('logging.Logger.info')
    mock_log_warning = mocker.patch('logging.Logger.warning')
    mock_log_error = mocker.patch('logging.Logger.error')

    logger.debug('[download] 50%')
    mock_log_info.assert_not_called()

    logger.debug('[info] Debug message')
    mock_log_info.assert_called_with('%s', 'Debug message')

    logger.warning('[warning] Warning message')
    mock_log_warning.assert_called_once_with('%s', 'Warning message')

    logger.error('[error] Error message')
    mock_log_error.assert_called_once_with('%s', 'Error message')

    logger.info('[info] Info message')
    mock_log_info.assert_called_with('%s', 'Info message')


def test_create_requests_session_no_domains_arg(mocker: MockerFixture) -> None:
    mock_extract_cookies = mocker.patch('yt_dlp_utils.lib.extract_cookies_from_browser')
    mocker.patch('requests.Session', return_value=mocker.Mock(headers={}))

    session = cast('Mock', setup_session(browser='chrome', profile='default'))

    mock_extract_cookies.assert_called_once_with('chrome', 'default')
    assert session.cookies.set.call_count == 0
    assert session.headers['user-agent'] == SHARED_HEADERS['user-agent']


def test_create_requests_session_with_default_headers(mocker: MockerFixture) -> None:
    cookie1 = mocker.Mock(value='value1', domain='example.com')
    cookie1.name = 'cookie1'
    mock_jar = mocker.Mock(spec=yt_dlp.cookies.YoutubeDLCookieJar)
    mock_jar.get_cookies_for_url.return_value = [cookie1]
    mock_extract_cookies = mocker.patch('yt_dlp_utils.lib.extract_cookies_from_browser',
                                        return_value=mock_jar)
    mocker.patch('requests.Session', return_value=mocker.Mock(headers={}))

    session = cast('Mock',
                   setup_session(browser='chrome', profile='default', domains=['example.com']))

    mock_extract_cookies.assert_called_once_with('chrome', 'default')
    session.cookies.set.assert_called_once_with(cookie1.name, cookie1.value, domain=cookie1.domain)

    assert session.headers['user-agent'] == SHARED_HEADERS['user-agent']


def test_create_requests_session_with_custom_headers(mocker: MockerFixture) -> None:
    cookie1 = mocker.Mock(value='value1', domain='example.com')
    cookie1.name = 'cookie1'
    mock_jar = mocker.Mock(spec=yt_dlp.cookies.YoutubeDLCookieJar)
    mock_jar.get_cookies_for_url.return_value = [cookie1]
    mock_extract_cookies = mocker.patch('yt_dlp_utils.lib.extract_cookies_from_browser',
                                        return_value=mock_jar)
    mocker.patch('requests.Session', return_value=mocker.Mock(headers={}))

    session = cast(
        'Mock',
        setup_session(browser='chrome',
                      profile='default',
                      domains=['example.com'],
                      headers={'Custom-Header': 'CustomValue'},
                      add_headers={'Another-Header': 'AnotherValue'}))

    mock_extract_cookies.assert_called_once_with('chrome', 'default')
    session.cookies.set.assert_called_once_with(cookie1.name, cookie1.value, domain=cookie1.domain)

    assert session.headers['Custom-Header'] == 'CustomValue'
    assert session.headers['Another-Header'] == 'AnotherValue'


def test_create_requests_session_with_retry(mocker: MockerFixture) -> None:
    cookie1 = mocker.Mock(value='value1', domain='example.com')
    cookie1.name = 'cookie1'
    cookie2 = mocker.Mock(value='value2', domain='youtube.com')
    cookie2.name = 'cookie2'
    cookie3 = mocker.Mock(value='value3', domain='example.com')
    cookie3.name = 'cookie3'
    cookie4 = mocker.Mock(value=1, domain='youtube.com')
    cookie4.name = 'cookie4'
    mock_jar = mocker.Mock(spec=yt_dlp.cookies.YoutubeDLCookieJar)
    mock_jar.get_cookies_for_url.side_effect = [[cookie1, cookie3], [cookie2, cookie4]]
    mock_extract_cookies = mocker.patch('yt_dlp_utils.lib.extract_cookies_from_browser',
                                        return_value=mock_jar)
    mocker.patch('requests.Session', return_value=mocker.Mock(headers={}))
    mock_adapter = mocker.patch('yt_dlp_utils.lib.HTTPAdapter')

    session = cast(
        'Mock',
        setup_session(browser='chrome',
                      profile='default',
                      domains=['example.com', '.youtube.com'],
                      setup_retry=True,
                      backoff_factor=0.5,
                      status_forcelist=[500, 502, 503]))
    mock_extract_cookies.assert_called_once_with('chrome', 'default')
    mock_adapter.assert_called_once_with(max_retries=mocker.ANY)
    session.cookies.set.assert_has_calls([
        mocker.call(cookie1.name, cookie1.value, domain=cookie1.domain),
        mocker.call(cookie3.name, cookie3.value, domain=cookie3.domain),
        mocker.call(cookie2.name, cookie2.value, domain=cookie2.domain)
    ])


def test_get_configured_yt_dlp_default(mocker: MockerFixture) -> None:
    mock_parse_options = mocker.patch('yt_dlp.parse_options', return_value=({}, {}, {}))
    mock_yt_dlp = mocker.patch('yt_dlp.YoutubeDL')

    get_configured_yt_dlp()

    mock_parse_options.assert_called_once()
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
    mock_parse_options = mocker.patch('yt_dlp.parse_options', return_value=({}, {}, {}))
    mock_yt_dlp = mocker.patch('yt_dlp.YoutubeDL')

    get_configured_yt_dlp(sleep_time=5, debug=True)

    mock_parse_options.assert_called_once()
    mock_yt_dlp.assert_called_once_with({
        'color': {
            'stdout': 'never',
            'stderr': 'never'
        },
        'logger': mocker.ANY,
        'sleep_interval_requests': 5,
        'verbose': True
    })


def test_get_configured_yt_dlp_with_custom_logger(mocker: MockerFixture) -> None:
    mock_parse_options = mocker.patch('yt_dlp.parse_options', return_value=({},))
    mock_yt_dlp = mocker.patch('yt_dlp.YoutubeDL')
    mocker.Mock()
    logger = mocker.Mock()

    get_configured_yt_dlp(logger=logger)

    mock_parse_options.assert_called_once()
    mock_yt_dlp.assert_called_once_with({
        'color': {
            'stdout': 'never',
            'stderr': 'never'
        },
        'logger': logger,
        'sleep_interval_requests': 3,
        'verbose': False
    })
