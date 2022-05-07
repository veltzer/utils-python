import config.project

package_name = config.project.project_name

install_requires = [
    "pymakehelper",
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
    "pylogconf",
]

dev_requires = [
    "pypitools",
    "Sphinx",
]

make_requires = [
    "pymakehelper",
    "pylint",
    "flake8",
]

test_requires = [
    "pytest",
    "pytest-cov",
    "pylint",
    "pyflakes",
    "flake8",
    "black",
]

python_requires = ">=3.9"
test_os = ["ubuntu-20.04"]
test_python = ["3.9"]
