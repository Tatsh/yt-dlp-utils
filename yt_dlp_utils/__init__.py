"""Utilities for programmatic use of yt-dlp."""
from __future__ import annotations

from .lib import YoutubeDLLogger, get_configured_yt_dlp, setup_session

__all__ = ('YoutubeDLLogger', 'get_configured_yt_dlp', 'setup_session')
__version__ = '0.0.3'
