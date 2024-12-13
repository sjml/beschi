from beschi.writers import all_writers, experimental_writers
from beschi.writer import Writer

def pytest_addoption(parser):
    parser.addoption("--experimental", action="store_const", const=True, default=False)
    parser.addoption("--skip", action="append", default=None)
    parser.addoption("--only", action="store", default=None)

def get_tested_writers(config) -> dict[str, type[Writer]]:
    aw = all_writers.copy()
    ew = experimental_writers.copy()
    skip = config.getoption("--skip")
    only = config.getoption("--only")
    exp  = config.getoption("--experimental")
    if skip and only:
        raise ValueError("Cannot specify both --skip and --only")
    if skip:
        for s in skip:
            if s not in aw and s not in ew:
                raise ValueError(f"No writer called '{s}' to skip!")
            if s in aw: del aw[s]
            if s in ew: del ew[s]
    if only:
        if only not in aw and only not in ew:
            raise ValueError(f"No writer called '{only}'!")
        if only in aw:
            aw = {only: aw[only]}
        else:
            aw = {}
        if only in ew:
            ew = {only: ew[only]}
        else:
            ew = {}

    usable_writers = aw
    if exp:
        usable_writers |= ew

    return usable_writers

def pytest_generate_tests(metafunc):
    if "generator_label" in metafunc.fixturenames:
        metafunc.parametrize("generator_label", get_tested_writers(metafunc.config).keys())
