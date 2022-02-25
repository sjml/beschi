from beschi.writers import all_writers, experimental_writers

def pytest_addoption(parser):
    parser.addoption("--experimental", action="store_const", const=True, default=False)
    parser.addoption("--skip", action="store", default=None)
    parser.addoption("--only", action="store", default=None)

def pytest_generate_tests(metafunc):
    if "generator_label" in metafunc.fixturenames:
        aw = all_writers.copy()
        ew = experimental_writers.copy()
        skip = metafunc.config.getoption("--skip")
        only = metafunc.config.getoption("--only")
        exp  = metafunc.config.getoption("--experimental")
        if skip and only:
            raise ValueError("Cannot specify both --skip and --only")
        if skip:
            if skip not in aw and skip not in ew:
                raise ValueError(f"No writer called '{skip}' to skip!")
            if skip in aw: del aw[skip]
            if skip in ew: del ew[skip]
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
        metafunc.parametrize("generator_label", usable_writers.keys())
