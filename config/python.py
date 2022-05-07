import config.project

package_name = config.project.project_name

dev_requires = [
    "pypitools",
    "Sphinx",
]
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
    "pyflakes",
    "pylogconf",
    "black",
]
make_requires = [
    "pymakehelper",
    "pylint",
    "flake8",
]

python_requires = ">=3.10"

test_os = ["ubuntu-22.04"]
test_python = ["3.10"]
