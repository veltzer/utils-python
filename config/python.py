""" python deps for this project """

import config.shared

install_requires: list[str] = [
    "jsonpickle",
    "PyGithub",
    "bsddb3",
    "progressbar",
    "chardet",
    "python-pptx",
    # this does not work
    # "python-apt",
    "pyyaml",
    "pytz",
    "python-dateutil",
    "ruamel.yaml",
    "yt-dlp",
]
build_requires: list[str] = config.shared.BUILD
test_requires: list[str] = config.shared.TEST
types_requires: list[str] = [
    "types-chardet",
    "types-PyYAML",
    "types-pytz",
    "types-python-dateutil",
]
requires = install_requires + build_requires + test_requires + types_requires
