'''
This is the config object for the jack+pulse scripts

    Mark Veltzer <mark@veltzer.net>
'''
import configparser # for ConfigParser
import os.path # for expanduser, isfile

mysection='jack_pulse'

def getConfig():
    inifile=os.path.expanduser('~/.jack_pulse.ini')
    if not os.path.isfile(inifile):
        print('inifile did not exist, writing it for the first time. find it in {inifile}'.format(**vars()))
        config=configparser.ConfigParser()
        config[mysection]={
            'do_midi_bridge': 'yes',
            'do_load_jack_module': 'yes',
            'do_route_jack': 'yes',
            'do_route_apps': 'yes',
        }
        with open(inifile, 'w') as configfile:
            config.write(configfile)
    config=configparser.ConfigParser()
    config.read(inifile)
    global do_midi_bridge, do_load_jack_module, do_route_jack, do_route_apps
    sect=config[mysection]
    do_midi_bridge=sect.getboolean('do_midi_bridge')
    do_load_jack_module=sect.getboolean('do_load_jack_module')
    do_route_jack=sect.getboolean('do_route_jack')
    do_route_apps=sect.getboolean('do_route_apps')
