#!/usr/bin/python3

import apt
import sys

cache = apt.Cache()
keep = 2

l = []
for pkg in apt.Cache():
    if pkg.is_installed:
        for x in pkg.versions:
            if 'linux-image' in x.provides:
                l.append(pkg.name)
print("found the following kernels: {}".format(l))
if len(l)<=keep:
    print("too few kernels installed, not doing anything")
    sys.exit(0)
else:
    print("have enough kernels to remove so proceeding")

l = sorted(l)
to_remove_list=l[:-keep]
for to_remove in to_remove_list:
    pkg = cache[to_remove]
    pkg.mark_delete(True, purge=True)
try:
    cache.commit()
    cache.close()
except Exception as e:
    print("Sorry, package removal failed [{}]".format(str(e)))
