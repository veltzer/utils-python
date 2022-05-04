import config.project

package_name = config.project.project_name

console_scripts = []

setup_requires = []

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
    "pydmt",
    "Sphinx",
    "pytest",
    "pytest-cov",
    "pylint",
    "pyflakes",
    "flake8",
    "black",
]

install_requires = list(setup_requires)
install_requires.extend(run_requires)

extras_require = {
}

python_requires = ">=3.9"
test_os = ["ubuntu-20.04"]
test_python = ["3.9"]
test_container = ["ubuntu:20.04"]
