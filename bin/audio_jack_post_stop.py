#!/usr/bin/python3

import os.path  # for expanduser
import os  # for kill
import jack_pulse.config  # for getConfig

options = jack_pulse.config.getConfig()
runfile = os.path.expanduser("~/.myjack_run")

if options["do_midi_bridge"]:
    with open(runfile, "r") as f:
        p1 = int(f.readline().rstrip())
        p2 = int(f.readline().rstrip())
    os.kill(p1, 9)
    os.kill(p2, 9)
