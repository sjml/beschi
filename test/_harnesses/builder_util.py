# little tiny build system
## doesn't do much, but make isn't flexible enough
##  and CMake/Scons/Meson/etc are to too heavy

import os
import argparse
import shutil

OUTPUT_DIR = "../../../out"
OUTPUT_BIN_DIR = os.path.join(OUTPUT_DIR, "executables")
INTERMEDIATE_DIR = os.path.join(OUTPUT_DIR, "intermediate")

def needs_build(target: str, depends_on: list[str] = []) -> bool:
    if not os.path.exists(target):
        return True
    target_age = os.stat(target).st_mtime
    for dep in depends_on:
        if not os.path.exists(dep):
            raise RuntimeError(f"File '{dep}' does not exist")
        if os.stat(dep).st_mtime > target_age:
            return True
    return False

def cleanup(files: list[str]):
    for f in files:
        if os.path.exists(f):
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.unlink(f)

class Builder:
    def __init__(self, language_name="") -> None:
        argparser = argparse.ArgumentParser()
        argparser.add_argument("--srcfile", type=str, required=True,  help="name of test harness file, relative to test/_harnesses/{language}")
        argparser.add_argument("--libfile", type=str, required=True,  help="name of generated message file, relative to out/generated/{language}")
        argparser.add_argument("--exename", type=str, required=False, help="name of executable, defaults to {srcfile_basename_lower}_{language_name}")
        argparser.add_argument("--clean",   dest="clean", action="store_true")
        argparser.set_defaults(clean=False)

        args = argparser.parse_args()
        self.should_clean = args.clean

        self.language_name = language_name
        self.libfile = args.libfile
        self.libname = os.path.splitext(self.libfile)[0]
        self.srcfile = args.srcfile
        self.srcname = os.path.splitext(self.srcfile)[0]
        self.exename = args.exename
        if self.exename == None:
            self.exename = f"{os.path.splitext(args.srcfile)[0].lower()}_{self.language_name}"
        self.exepath = os.path.join(OUTPUT_BIN_DIR, self.exename)

        self.generated_code_dir = os.path.join(OUTPUT_DIR, "generated", self.language_name)
        self.gen_file = os.path.join(self.generated_code_dir, self.libfile)


    def build(self):
        base = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.language_name)
        os.chdir(base)

        for d in [OUTPUT_BIN_DIR, INTERMEDIATE_DIR]:
            if not os.path.exists(d):
                os.makedirs(d)

    def clean(self):
        base = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.language_name)
        os.chdir(base)

        cleanup([self.exepath])
