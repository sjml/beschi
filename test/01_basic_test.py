import shutil
import subprocess

import beschi.writers
from beschi.cli import VERSION_STRING


# will assert if a writer doesn't exist
# or is missing its namesake class or LANGUAGE_NAME
def test_list_writers(generator_label):
    try:
        writer = beschi.writers.all_writers[generator_label]
    except KeyError:
        writer = beschi.writers.experimental_writers[generator_label]
    assert(issubclass(writer, beschi.writer.Writer))

# see if the executable version works
def test_cli_exists():
    assert(shutil.which("beschi") != None)

# make sure we're testing the version in this directory
def test_version():
    exe_version = subprocess.check_output(["beschi", "--version"]).decode("utf-8").strip()
    assert(exe_version == VERSION_STRING)
