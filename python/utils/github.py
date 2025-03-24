"""
github utilities
"""


import configparser
import os.path
import github


inifile = os.path.expanduser('~/.details.ini')
config = configparser.ConfigParser()
config.read(inifile)
opt_username = config.get('github','username')


def get_nonforked_repos():
    g = github.Github()
    for repo in g.get_user(opt_username).get_repos():
        if not repo.fork:
            yield repo


def print_it(f):
    def new_function():
        print(f"[{f.__name__}] starting...")
        r = f()
        print(f"[{f.__name__}] ending...")
        return r
    return new_function


@print_it
def get_nonforked_repos_list():
    return list(get_nonforked_repos())
