from typing import List


config_requires: List[str] = []
dev_requires: List[str] = [
]
install_requires: List[str] = [
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
build_requires: List[str] = [
    "pydmt",
    "pymakehelper",
    "pycmdtools",
    "pyclassifiers",
]
test_requires: List[str] = [
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
requires = config_requires + install_requires + build_requires + test_requires
