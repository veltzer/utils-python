from typing import List


config_requires: List[str] = []
dev_requires: List[str] = [
    "black",
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
]
build_requires: List[str] = [
    "pymakehelper",
    "pydmt",
    "pycmdtools",
    "pyclassifiers",
]
test_requires: List[str] = [
    "pylint",
    "pytest",
    "pytest-cov",
    "flake8",
    "pyflakes",
    "mypy",
    "types-chardet",
    "types-PyYAML",
]
requires = config_requires + install_requires + build_requires + test_requires
