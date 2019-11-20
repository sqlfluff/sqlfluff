""" module for loading config """

import configparser
import os

from .dialects import dialect_selector
from .templaters import templater_selector


# We define a global loader, so that between calls to load config, we
# can still cache appropriately
global_loader = None


def nested_combine(*dicts):
    r = {}
    for d in dicts:
        for k in d:
            if k in r and isinstance(r[k], dict):
                if isinstance(d[k], dict):
                    r[k] = nested_combine(r[k], d[k])
                else:
                    raise ValueError("Key {0!r} is a dict in one config but not another! PANIC: {1!r}".format(k, d[k]))
            else:
                r[k] = d[k]
    return r


def dict_diff(left, right):
    buff = {}
    for k in left:
        # Is the key there at all?
        if k not in right:
            buff[k] = left[k]
        # Is the content the same?
        elif left[k] == right[k]:
            continue
        # If it's not the same but both are dicts, then compare
        elif isinstance(left[k], dict) and isinstance(right[k], dict):
            diff = dict_diff(left[k], right[k])
            buff[k] = diff
        # It's just different
        else:
            buff[k] = left[k]
    return buff


class ConfigLoader(object):
    """ the class for loading config files """
    def __init__(self):
        # TODO: check that this cache implementation is actually useful
        self._config_cache = {}

    @classmethod
    def get_global(cls):
        """ Get the singleton loader """
        global global_loader
        if not global_loader:
            global_loader = cls()
        return global_loader

    def load_config_at_path(self, path):
        # First check the cache
        if str(path) in self._config_cache:
            return self._config_cache[str(path)]

        # The potential filenames we would look for at this path.
        # NB: later in this list overwrites earlier
        filename_options = ['setup.cfg', 'tox.ini', 'pep8.ini', '.sqlfluff']

        c = {}

        if os.path.isdir(path):
            p = path
        else:
            p = os.path.dirname(path)

        d = os.listdir(p)
        # iterate this way round to make sure things overwrite is the right direction
        for fname in filename_options:
            if fname in d:
                config = configparser.ConfigParser()
                config.read(os.path.join(p, fname))
                for k in config.sections():
                    if k == 'sqlfluff':
                        key = 'core'
                    elif k.startswith('sqlfluff:'):
                        key = k[len('sqlfluff:'):]
                    else:
                        # if it doesn't start with sqlfluff, then don't go
                        # further on this iteration
                        continue

                    if key not in c:
                        c[key] = {}

                    for name, val in config.items(section=k):
                        # Try to coerce it to a more specific type,
                        # otherwise just make it a string.
                        try:
                            v = int(val)
                        except ValueError:
                            try:
                                v = float(val)
                            except ValueError:
                                if val in ['True', 'False']:
                                    v = bool(val)
                                else:
                                    v = val
                        c[key][name] = v

        # Store in the cache
        self._config_cache[str(path)] = c
        return c

    def load_user_config(self):
        user_home_path = os.path.expanduser("~")
        return self.load_config_at_path(user_home_path)

    def load_config_up_to_path(self, path):
        """ an extention of the above which loads a selection of config files """
        user_config = self.load_user_config()

        working_path = os.getcwd()
        given_path = os.path.abspath(path)
        # If we've been passed a file and not a directory,
        # then go straight to the directory.
        if not os.path.isdir(given_path):
            given_path = os.path.dirname(given_path)
        config_stack = []

        if hasattr(os.path, 'commonpath'):
            common_path = os.path.commonpath([working_path, given_path])
        else:
            # Compatabilty with pre python 3.5
            common_path = os.path.commonprefix([working_path, given_path])

        if common_path == working_path:
            # we have a sub path! We can load nested paths
            last_path = given_path
            while True:
                config_stack.insert(0, self.load_config_at_path(last_path))
                if last_path == working_path:
                    break
                # iterate up the directories
                if last_path == os.path.dirname(last_path):
                    # we're not making progres...
                    # [prevent infinite loop]
                    break
                last_path = os.path.dirname(last_path)
            config_stack.insert(0, self.load_config_at_path(working_path))
        else:
            # we have divergent paths, we can only load config for that path and global
            config_stack.append(self.load_config_at_path(given_path))

        # The lowest priority is the user config, then increasingly the configs closest
        # to the file being directly linted.
        return nested_combine(user_config, *config_stack)


class FluffConfig(object):
    """ The class that actually gets passed around as a config object """
    defaults = {'core': {
        'verbose': 0,
        'nocolor': False,
        'dialect': 'ansi',
        'templater': 'jinja',
        'rules': None,
        'exclude_rules': None,
        'recurse': 0
    }}

    def __init__(self, configs=None, overrides=None):
        self._overrides = overrides  # We only store this for child configs
        self._configs = nested_combine(
            self.defaults,
            configs or {'core': {}},
            {'core': overrides or {}})
        # Some configs require special treatment
        self._configs['core']['color'] = False if self._configs['core']['nocolor'] else None
        # Whitelists and blacklists
        if self._configs['core']['rules']:
            self._configs['core']['rule_whitelist'] = self._configs['core']['rules'].split(',')
        else:
            self._configs['core']['rule_whitelist'] = None
        if self._configs['core']['exclude_rules']:
            self._configs['core']['rule_blacklist'] = self._configs['core']['exclude_rules'].split(',')
        else:
            self._configs['core']['rule_blacklist'] = None
        # Configure Recursion
        if self._configs['core']['recurse'] == 0:
            self._configs['core']['recurse'] = True
        # Dialect and Template selection
        self._configs['core']['dialect_obj'] = dialect_selector(self._configs['core']['dialect'])
        self._configs['core']['templater_obj'] = templater_selector(self._configs['core']['templater'])

    @classmethod
    def from_root(cls, overrides=None):
        """ loads a config object just based on the root directory """
        loader = ConfigLoader.get_global()
        c = loader.load_user_config()
        return cls(configs=c, overrides=overrides)

    @classmethod
    def from_path(cls, path, overrides=None):
        """ loads a config object given a particular path """
        loader = ConfigLoader.get_global()
        c = loader.load_config_up_to_path(path=path)
        return cls(configs=c, overrides=overrides)

    def make_child_from_path(self, path):
        """ Make a new child config at a path but pass on overrides """
        return self.from_path(path, overrides=self._overrides)

    def diff_to(self, other):
        """ Returns a filtered dict of items in this config that are not in the other
        or are different to the other """
        return dict_diff(self._configs, other._configs)

    def get(self, val, section='core'):
        return self._configs[section].get(val, None)

    def get_section(self, section):
        return self._configs.get(section, None)
