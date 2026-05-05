local utils = import 'utils.libjsonnet';

{
  uses_user_defaults: true,
  description: 'Utilities for programmatic use of yt-dlp.',
  keywords: ['command line', 'yt-dlp'],
  project_name: 'yt-dlp-utils',
  version: '0.1.1',
  security_policy_supported_versions: { '0.1.x': ':white_check_mark:' },
  pyproject+: {
    tool+: {
      poetry+: {
        dependencies+: {
          niquests: {
            optional: true,
            version: utils.latestPypiPackageVersionCaret('niquests'),
          },
          requests: utils.latestPypiPackageVersionCaret('requests'),
          'urllib3-future': {
            optional: true,
            version: utils.latestPypiPackageVersionCaret('urllib3-future'),
          },
          'yt-dlp': { extras: ['default'], version: utils.latestPypiPackageVersionCaret('yt-dlp') },
        },
        extras: {
          asyncio: ['niquests', 'urllib3-future'],
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
              niquests: utils.latestPypiPackageVersionCaret('niquests'),
              'pytest-asyncio': utils.latestPypiPackageVersionCaret('pytest-asyncio'),
              'urllib3-future': utils.latestPypiPackageVersionCaret('urllib3-future'),
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
}
