"""
Bare minimum settings for collecting production assets.
"""
from ..common import *
from openedx.core.lib.derived import derive_settings

ENABLE_COMPREHENSIVE_THEMING = True
COMPREHENSIVE_THEME_DIRS.append('/openedx/themes')
COMPREHENSIVE_THEME_LOCALE_PATHS = [
	"/openedx/themes/cmm-openedx/conf/locale",
	"/openedx/themes/eol-uchile-2020/conf/locale",
	"/openedx/themes/edx-uabierta/conf/locale",
	"/openedx/themes/virtual-labx-cla-theme/conf/locale",
	"/openedx/themes/virtual-labx-theme/conf/locale",
	"/openedx/themes/redfid-theme/conf/locale",
	"/openedx/themes/alpha-project-theme/conf/locale"
]
STATIC_ROOT_BASE = '/openedx/staticfiles'
STATIC_ROOT = path(STATIC_ROOT_BASE) / 'studio'
WEBPACK_LOADER['DEFAULT']['STATS_FILE'] = STATIC_ROOT / "webpack-stats.json"

SECRET_KEY = 'secret'
XQUEUE_INTERFACE = {
    'django_auth': None,
    'url': None,
}
DATABASES = {
    "default": {},
}
derive_settings(__name__)
