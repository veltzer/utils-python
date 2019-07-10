import github # for Github
import configparser # for ConfigParser
import os.path # for expanduser

inifile=os.path.expanduser('~/.details.ini')
config=configparser.ConfigParser()
config.read(inifile)
opt_username=config.get('github','username')

def get_nonforked_repos():
    g=github.Github()
    for repo in g.get_user(opt_username).get_repos():
        if not repo.fork:
            yield repo

def print_it(f):
    def new_function():
        print('[{0}] starting...'.format(f.__name__))
        r=f()
        print('[{0}] ending...'.format(f.__name__))
        return r
    return new_function

@print_it
def get_nonforked_repos_list():
    return [repo for repo in get_nonforked_repos()]
