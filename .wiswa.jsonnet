(import 'defaults.libjsonnet') + {
  // Project-specific
  description: 'Utilities for programmatic use of yt-dlp.',
  keywords: ['command line', 'yt-dlp'],
  project_name: 'yt-dlp-utils',
  version: '0.0.3',
  citation+: {
    'date-released': '2025-04-25',
  },
  pyproject+: {
    tool+: {
      poetry+: {
        dependencies+: {
          requests: '^2.32.3',
          'yt-dlp': { extras: ['default'], version: '^2025.3.31' },
        },
        group+: {
          dev+: {
            dependencies+: {
              'types-requests': '^2.32.0.20250328',
              'yt-dlp-types': '^0',
            },
          },
        },
      },
    },
  },
  // Common
  authors: [
    {
      'family-names': 'Udvare',
      'given-names': 'Andrew',
      email: 'audvare@gmail.com',
      name: '%s %s' % [self['given-names'], self['family-names']],
    },
  ],
  local funding_name = '%s2' % std.asciiLower(self.github_username),
  github_username: 'Tatsh',
  github+: {
    funding+: {
      ko_fi: funding_name,
      liberapay: funding_name,
      patreon: funding_name,
    },
  },
}
