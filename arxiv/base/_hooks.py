"""WIP: config hooks for Flask apps."""

from typing import Any, List, Callable, Mapping, Optional
from collections import defaultdict
from itertools import chain

from flask import Config, Flask

Callback = Callable[['ConfigWithHooks', str, Any], None]


class ConfigWithHooks(Config):
    """Config object that has __setitem__ hooks."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Make a place for hooks on init."""
        super(ConfigWithHooks, self).__init__(*args, **kwargs)
        self._hooks: Mapping[str, List[Callback]] = defaultdict(list)

    def add_hook(self, key: Optional[str], hook: Callback) -> None:
        """
        Add a callback/hook for a config key.

        The hook will be called when the ``key`` is set.
        """
        if key is None:
            key = '__all__'
        self._hooks[key].append(hook)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set a config ``key``, and call registered hooks."""
        super(ConfigWithHooks, self).__setitem__(key, value)
        for hook in chain(self._hooks.get(key, []), self._hooks['__all__']):
            hook(self, key, value)


class FlaskWithConfigHooks(Flask):
    """Extends :class:`.Flask` to use :class:`.ConfigWithHooks`."""

    config_class = ConfigWithHooks


def update_elasticsearch_config(config: Mapping, key: str, value: Any) -> None:
    """Propagate changes in config values to related config parameters."""
    _hooks = dict([
        ('ELASTICSEARCH_SERVICE_HOST', 'ELASTICSEARCH_HOST'),
        ('ELASTICSEARCH_SERVICE_PORT', 'ELASTICSEARCH_PORT'),
        ('ELASTICSEARCH_PORT_%s_PROTO' % config['ELASTICSEARCH_PORT'],
         'ELASTICSEARCH_SCHEME'),
    ])
    if key in _hooks:
        config[_hooks[key]] = value
