import os
ROOT_PATH = os.path.join(os.path.dirname(__file__))
# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
)
TEMPLATE_DIRS = (
        os.path.join(ROOT_PATH, 'templates'),
        )

