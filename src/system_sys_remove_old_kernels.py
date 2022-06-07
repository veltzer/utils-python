#!/usr/bin/python3

import sys

# import apt

# cache = apt.Cache()
cache = {}
keep = 2

pkg_list = []
for pkg in cache:
    if pkg.is_installed:
        for x in pkg.versions:
            if "linux-image" in x.provides:
                pkg_list.append(pkg.name)
print(f"found the following kernels: {pkg_list}")
if len(pkg_list) <= keep:
    print("too few kernels installed, not doing anything")
    sys.exit(0)
else:
    print("have enough kernels to remove so proceeding")

pkg_list = sorted(pkg_list)
to_remove_list = pkg_list[:-keep]
for to_remove in to_remove_list:
    pkg = cache[to_remove]
    pkg.mark_delete(True, purge=True)
# pylint: disable=broad-except
try:
    # cache.commit()
    # cache.close()
    pass
except Exception as e:
    print(f"Sorry, package removal failed [{e}]")
