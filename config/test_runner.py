"""Test runner that swaps the staticfiles storage during tests.

The WhiteNoise manifest storage needs `collectstatic` output, which tests
don't have (and shouldn't need): rendering {% static %} would raise
"Missing staticfiles manifest entry". Swapping the storage here, instead
of sniffing sys.argv in settings.py, works no matter how the suite is
invoked.
"""

from django.test.runner import DiscoverRunner
from django.test.utils import override_settings

_TEST_STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}


class CookbookTestRunner(DiscoverRunner):
    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        self._storages_override = override_settings(STORAGES=_TEST_STORAGES)
        self._storages_override.enable()

    def teardown_test_environment(self, **kwargs):
        self._storages_override.disable()
        super().teardown_test_environment(**kwargs)
