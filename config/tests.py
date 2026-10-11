"""Tests for environment-driven settings in config/settings.py."""

import importlib
import os
from unittest import mock

from django.conf import settings as django_settings
from django.test import SimpleTestCase

from config import settings as settings_module
from config.settings import env_bool


class EnvBoolTests(SimpleTestCase):
    """env_bool parses an environment variable into a boolean."""

    def _with_env(self, name, value):
        return mock.patch.dict(os.environ, {name: value})

    def test_returns_default_when_unset(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertIs(env_bool('MISSING_VAR', True), True)
            self.assertIs(env_bool('MISSING_VAR', False), False)

    def test_falsey_strings_mean_off(self):
        for value in ('0', 'false', 'False', 'FALSE', 'no', 'off', ''):
            with self._with_env('FLAG', value):
                self.assertIs(env_bool('FLAG', True), False, msg=repr(value))

    def test_truthy_strings_mean_on(self):
        for value in ('1', 'true', 'True', 'yes', 'on'):
            with self._with_env('FLAG', value):
                self.assertIs(env_bool('FLAG', False), True, msg=repr(value))


class SettingsEnvOverrideTests(SimpleTestCase):
    """SECRET_KEY, DEBUG, and ALLOWED_HOSTS come from the environment,
    with the development values as defaults."""

    ENV_KEYS = ('SECRET_KEY', 'DEBUG', 'ALLOWED_HOSTS')

    def reload_settings(self, env):
        """Reload config.settings with only the given env overrides set."""
        clean = {k: v for k, v in os.environ.items() if k not in self.ENV_KEYS}
        clean.update(env)
        with mock.patch.dict(os.environ, clean, clear=True):
            return importlib.reload(settings_module)

    def tearDown(self):
        # Restore the module to match the real environment.
        importlib.reload(settings_module)

    def test_dev_defaults_without_env_vars(self):
        module = self.reload_settings({})
        self.assertTrue(module.DEBUG)
        self.assertTrue(module.SECRET_KEY.startswith('django-insecure-'))
        self.assertEqual(module.ALLOWED_HOSTS, [])

    def test_env_vars_override_defaults(self):
        module = self.reload_settings({
            'SECRET_KEY': 'a-secret-from-the-environment',
            'DEBUG': 'False',
            'ALLOWED_HOSTS': 'example.com, www.example.com',
        })
        self.assertEqual(module.SECRET_KEY, 'a-secret-from-the-environment')
        self.assertFalse(module.DEBUG)
        self.assertEqual(module.ALLOWED_HOSTS, ['example.com', 'www.example.com'])

    def test_debug_zero_means_off(self):
        module = self.reload_settings({'DEBUG': '0'})
        self.assertFalse(module.DEBUG)


class WhiteNoiseConfigurationTests(SimpleTestCase):
    """WhiteNoise middleware and static file storage are wired up."""

    def test_whitenoise_directly_after_security_middleware(self):
        middleware = django_settings.MIDDLEWARE
        security_index = middleware.index(
            'django.middleware.security.SecurityMiddleware')
        self.assertEqual(
            middleware[security_index + 1],
            'whitenoise.middleware.WhiteNoiseMiddleware')

    def test_static_root_configured(self):
        self.assertEqual(
            django_settings.STATIC_ROOT,
            django_settings.BASE_DIR / 'staticfiles')

    def test_whitenoise_storage_backend(self):
        self.assertEqual(
            django_settings.STORAGES['staticfiles']['BACKEND'],
            'whitenoise.storage.CompressedManifestStaticFilesStorage')
