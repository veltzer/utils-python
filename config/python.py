make_requires = [
    "pymakehelper",
]
install_requires = [
    "jsonpickle",
    "PyGithub",
    "bsddb3",
    "progressbar",
    "chardet",
    # this does not work
    # "python-apt",
]
test_requires = [
    "pylint",
    "pytest",
    "pytest-cov",
    "flake8",
    "pyflakes",
    "black",
]

python_requires = ">=3.10"

test_os = ["ubuntu-22.04"]
test_python = ["3.10"]
