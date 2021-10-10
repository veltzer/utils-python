"""
This is the config object for the jack+pulse scripts
"""

import configparser
import os.path


mysection = 'jack_pulse'


def getConfig():
    inifile = os.path.expanduser('~/.jack_pulse.ini')
    if not os.path.isfile(inifile):
        print(f"inifile did not exist, writing it for the first time. find it in {inifile}")
        config = configparser.ConfigParser()
        config[mysection] = {
            'do_midi_bridge': 'yes',
            'do_load_jack_module': 'yes',
            'do_route_jack': 'yes',
            'do_route_apps': 'yes',
        }
        with open(inifile, 'w') as configfile:
            config.write(configfile)
    config = configparser.ConfigParser()
    config.read(inifile)
    sect = config[mysection]
    options = {}
    options["do_midi_bridge"] = sect.getboolean('do_midi_bridge')
    options["do_load_jack_module"] = sect.getboolean('do_load_jack_module')
    options["do_route_jack"] = sect.getboolean('do_route_jack')
    options["do_route_apps"] = sect.getboolean('do_route_apps')
    return options
