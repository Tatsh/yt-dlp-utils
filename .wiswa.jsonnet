local utils = import 'utils.libjsonnet';

{
  description: 'Utilities for programmatic use of yt-dlp.',
  keywords: ['command line', 'yt-dlp'],
  project_name: 'yt-dlp-utils',
  version: '0.0.7',
  pyproject+: {
    tool+: {
      poetry+: {
        dependencies+: {
          aiohttp: {
            optional: true,
            version: utils.latestPypiPackageVersionCaret('aiohttp'),
          },
          'aiohttp-retry': {
            optional: true,
            version: utils.latestPypiPackageVersionCaret('aiohttp-retry'),
          },
          requests: utils.latestPypiPackageVersionCaret('requests'),
          'yt-dlp': { extras: ['default'], version: utils.latestPypiPackageVersionCaret('yt-dlp') },
        },
        extras: {
          asyncio: ['aiohttp', 'aiohttp-retry'],
        },
        group+: {
          dev+: {
            dependencies+: {
              'types-requests': utils.latestPypiPackageVersionCaret('types-requests'),
              'types-yt-dlp': utils.latestPypiPackageVersionCaret('types-yt-dlp'),
            },
          },
          tests+: {
            dependencies+: {
              aiohttp: utils.latestPypiPackageVersionCaret('aiohttp'),
              'aiohttp-retry': utils.latestPypiPackageVersionCaret('aiohttp-retry'),
              'pytest-asyncio': utils.latestPypiPackageVersionCaret('pytest-asyncio'),
              yarl: utils.latestPypiPackageVersionCaret('yarl'),
            },
          },
        },
      },
      pytest+: {
        ini_options+: {
          asyncio_default_fixture_loop_scope: 'function',
          asyncio_mode: 'auto',
        },
      },
    },
  },
  copilot+: {
    intro: 'yt-dlp-utils is a library to ease use of yt-dlp.',
  },
}
