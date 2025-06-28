""" python deps for this project """

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
]
build_requires: list[str] = [
    "pydmt",
    "pymakehelper",
    "pycmdtools",
    "pyclassifiers",
]
test_requires: list[str] = [
    "pylint",
    "pytest",
    "pytest-cov",
    "mypy",
    # types
    "types-chardet",
    "types-PyYAML",
    "types-pytz",
    "types-python-dateutil",
]
requires = install_requires + build_requires + test_requires
