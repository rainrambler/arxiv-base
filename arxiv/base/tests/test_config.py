"""Test configuration behavior."""

from unittest import TestCase, mock
import os
from ..factory import create_ui_web_app, FlaskWithConfigHooks
from .. import config


class TestHooks(TestCase):
    """Test :func:`.factory.FlaskWithConfigHooks`."""

    def test_hook_on_specific_key(self):
        """Add a hook for a specific config key."""
        mock_callback = mock.MagicMock()
        app = FlaskWithConfigHooks('test_app')
        app.config['FOO_PARAM'] = 'bar'

        app.config.add_hook('FOO_PARAM', mock_callback)

        app.config['FOO_PARAM'] = 'baz'
        app.config['OTHER_PARAM'] = True
        self.assertEqual(mock_callback.call_count, 1,
                         'Callback is only called once because it is specific')
        self.assertEqual(mock_callback.call_args[0],
                         (app.config, 'FOO_PARAM', 'baz'),
                         'Callback is called with the specific key for which'
                         ' it is registered, and the new value.')

    def test_hook_on_any_key(self):
        """Add a hook for a specific config key."""
        mock_callback = mock.MagicMock()
        app = FlaskWithConfigHooks('test_app')
        app.config['FOO_PARAM'] = 'bar'

        app.config.add_hook(None, mock_callback)

        app.config['FOO_PARAM'] = 'baz'
        app.config['OTHER_PARAM'] = True
        self.assertEqual(mock_callback.call_count, 2,
                         'Callback is called twice because it is not specific')
        self.assertEqual(mock_callback.call_args[0],
                         (app.config, 'OTHER_PARAM', True),
                         'Last call was for OTHER_PARAM.')


class TestElasticsearchHooks(TestCase):
    """Test :func:`.config.update_elasticsearch_config`."""

    def test_elasticsearch_config_hook(self):
        """The config hook is registered."""
        app = FlaskWithConfigHooks('test_app')
        os.environ['ELASTICSEARCH_SERVICE_HOST'] = 'foohost'
        os.environ['ELASTICSEARCH_SERVICE_PORT'] = '1234'
        os.environ['ELASTICSEARCH_PORT_1234_PROTO'] = 'gopher'
        app.config.from_pyfile('../config.py')

        self.assertEqual('ELASTICSEARCH_HOST')

        app.config.add_hook(config.update_elasticsearch_config)
        app.config['ELASTICSEARCH_SERVICE_HOST'] = 'foohost'
