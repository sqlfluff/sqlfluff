""" module for loading config """

import configparser
import os


def nested_combine(*dicts):
    print(dicts)
    r = {}
    for d in dicts:
        for k in d:
            if k in r and isinstance(r[k], dict):
                if isinstance(d[k], dict):
                    r[k] = nested_combine(r[k], d[k])
                else:
                    raise ValueError("Key {0!r} is a dict in one config but not another! PANIC".format(k))
            else:
                r[k] = d[k]
    print(r)
    return r


class ConfigLoader(object):
    """ the class for loading config files """
    def __init__(self):
        pass

    def load_config_at_path(self, path):
        # The potential filenames we would look for at this path.
        filename_options = ['.sqlfluff', 'tox.ini', 'setup.cfg']

        c = {}

        if os.path.isdir(path):
            p = path
        else:
            p = os.path.dirname(path)

        for fname in os.listdir(p):
            if fname in filename_options:
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
                    c[key] = {}
                    for name, val in config.items(section=k):
                        try:
                            v = int(val)
                        except ValueError:
                            try:
                                v = float(val)
                            except ValueError:
                                v = val
                        c[key][name] = v
        return c

    def load_config_up_to_path(self, path):
        """ an extention of the above which loads a selection of config files """
        user_home_path = os.path.expanduser("~")
        user_config = self.load_config_at_path(user_home_path)

        working_path = os.getcwd()
        given_path = os.path.abspath(path)
        config_stack = []

        common_path = os.path.commonpath([working_path, given_path])
        if common_path == working_path:
            # we have a sub path! We can load nested paths
            last_path = given_path
            while True:
                config_stack.insert(0, self.load_config_at_path(last_path))
                # iterate up the directories
                last_path = os.path.dirname(last_path)
                if last_path == working_path:
                    break
            config_stack.insert(0, self.load_config_at_path(working_path))
        else:
            # we have divergent paths, we can only load config for that path and global
            config_stack.append(self.load_config_at_path(given_path))

        return nested_combine(user_config, *config_stack)
