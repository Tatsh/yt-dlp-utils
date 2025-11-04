local utils = import 'utils.libjsonnet';

{
  description: 'Utilities for programmatic use of yt-dlp.',
  keywords: ['command line', 'yt-dlp'],
  project_name: 'yt-dlp-utils',
  version: '0.0.5',
  pyproject+: {
    tool+: {
      poetry+: {
        dependencies+: {
          requests: utils.latestPypiPackageVersionCaret('requests'),
          'yt-dlp': { extras: ['default'], version: utils.latestPypiPackageVersionCaret('yt-dlp') },
        },
        group+: {
          dev+: {
            dependencies+: {
              'types-requests': utils.latestPypiPackageVersionCaret('types-requests'),
              'types-yt-dlp': utils.latestPypiPackageVersionCaret('types-yt-dlp'),
            },
          },
        },
      },
    },
  },
  copilot+: {
    intro: 'yt-dlp-utils is a library to ease use of yt-dlp.',
  },
}
