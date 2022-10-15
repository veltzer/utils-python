#!/usr/bin/python3

"""
This script serves as post jack start script to route pulseaudio to jack...

References:
http://askubuntu.com/questions/71863/how-to-change-pulseaudio-sink-with-pacmd-set-default-sink-during-playback
http://docs.fedoraproject.org/en-US/Fedora_Draft_Documentation/0.1/html/Musicians_Guide/sect-Musicians_Guide-Integrating_PulseAudio_with_JACK.html
https://github.com/jackaudio/jackaudio.github.com/wiki/WalkThrough_User_PulseOnJack
http://trac.jackaudio.org/wiki/WalkThrough/User/PulseOnJack
http://superuser.com/questions/210617/how-to-automatically-set-pulseaudio-default-sink-to-remote-server-at-boot-ubun

TODO:
- make a post about it...
"""

import os.path
import subprocess
import re
import jack_pulse.config  # type: ignore


def get_sinks():
    with subprocess.Popen(
        ["pacmd", "list-sink-inputs"], stdout=subprocess.PIPE
    ) as pout:
        myre = re.compile(r"^\s+index: (\d+)\n$")
        for line in pout.stdout:
            mymatch = myre.match(line)
            if mymatch:
                yield int(mymatch.group(1))


options = jack_pulse.config.getConfig()
runfile = os.path.expanduser("~/.myjack_run")
if options["do_midi_bridge"]:
    with subprocess.Popen("a2jmidi_bridge") as p1, subprocess.Popen(
        "j2amidi_bridge"
    ) as p2:
        with open(runfile, "w") as f:
            f.write(str(p1.pid) + "\n")
            f.write(str(p2.pid) + "\n")
    if options["do_load_jack_module"]:
        subprocess.check_call(
            ["pactl", "load-module", "module-jack-sink", "channels=2"],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        )
if options["config.do_route_jack"]:
    subprocess.check_call(
        ["pacmd", "set-default-sink", "jack_out"],
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
    )
if options["do_route_apps"]:
    for index in get_sinks():
        subprocess.check_call(
            ["pacmd", "move-sink-input", str(index), "jack_out"],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        )
