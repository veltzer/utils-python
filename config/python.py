import config.project

package_name = config.project.project_name

run_requires = [
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
    "pymakehelper",
    "pylint",
    "pytest",
    "pytest-cov",
    "flake8",
    "pylogconf",
]

dev_requires = [
    "pyclassifiers",
    "pypitools",
    "Sphinx",
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
