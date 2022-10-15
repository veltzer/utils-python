#!/usr/bin/python3

import os.path
import os
import jack_pulse.config  # type: ignore

options = jack_pulse.config.getConfig()
runfile = os.path.expanduser("~/.myjack_run")

if options["do_midi_bridge"]:
    with open(runfile, "r") as f:
        p1 = int(f.readline().rstrip())
        p2 = int(f.readline().rstrip())
    os.kill(p1, 9)
    os.kill(p2, 9)
