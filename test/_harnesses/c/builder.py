import os
import stat
import platform
import subprocess

# i hate this
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import builder_util

CC = "clang"
CXX = "clang++"

FLAGS = [
    "-pedantic-errors", # complain if compiler extensions come into play
    "-Weverything",     # actually, complain about everything
    "-Werror",          # loudly
    "-O0", "-g",        # have as much debug info as we can
]
SILENCE_WARNINGS = [    # turn off these very specific warnings, though
    "float-equal",      # doing comparisons in the test harness; actually *do* want to to check identical
    "padded",           # automatically optimizing struct layout is a hard problem :(
    "unused-parameter", # GetSizeInBytes takes a message pointer, but never looks at it if the size is constant precomputed
]
[FLAGS.append(f"-Wno-{sw}") for sw in SILENCE_WARNINGS]
CFLAGS = [
    "-std=c99",         # c99 is the baseline
]
CSILENCE_WARNINGS = [
]
[CFLAGS.append(f"-Wno-{sw}") for sw in CSILENCE_WARNINGS]

CPPFLAGS = [
    "-std=c++11",       # c++11 is the baseline
]
CPPSILENCE_WARNINGS = [
    # since this code is meant to be usable from C primarily,
    #   need to silence some warnings that demand more modern C++
    "c99-extensions", # don't get *that* pedantic
    "old-style-cast", # let us use c-style casts without complaining
    "zero-as-null-pointer-constant", # otherwise have to use nullptr, or redefine it, which feels like code smell
    "cast-qual", # really wish I could only silence this for string literals
]
[CPPFLAGS.append(f"-Wno-{sw}") for sw in CPPSILENCE_WARNINGS]


class CBuilder(builder_util.Builder):
    def __init__(self) -> None:
        super().__init__("c")
        if self.srcfile.endswith(".h"):
            self.srcfile = f"{self.srcfile[:-2]}.c"
        self.exepath_cpp = f"{self.exepath}pp"
        self.intermediate_path = os.path.join(builder_util.INTERMEDIATE_DIR, self.exename)
        self.intermediate_path_cpp = f"{self.intermediate_path}pp"

    def build(self):
        super().build()

        build_flags = FLAGS
        build_flags += [f"-I{os.path.dirname(self.gen_file)}"]
        if platform.system() == "Darwin":
            build_flags += ["-isysroot", "/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk"]

        deps = [self.srcfile, self.gen_file, "util.h"]
        if builder_util.needs_build(self.intermediate_path, deps):
            subprocess.check_call([
                CC, *build_flags,
                *CFLAGS,
                "-o", self.intermediate_path,
                self.srcfile
            ])
        if builder_util.needs_build(self.intermediate_path_cpp, deps):
            subprocess.check_call([
                CXX, *build_flags,
                *CPPFLAGS,
                "-o", self.intermediate_path_cpp,
                "-x", "c++", self.srcfile
            ])

        if builder_util.needs_build(self.exepath, [self.intermediate_path]):
            shim = open("./exe_template").read()
            shim = shim.replace("{# EXE_NAME #}", self.exename)
            with open(self.exepath, "w") as shim_file:
                shim_file.write(shim)
            os.chmod(self.exepath, os.stat(self.exepath).st_mode | stat.S_IEXEC)

        if builder_util.needs_build(self.exepath_cpp, [self.intermediate_path_cpp]):
            shim = open("./exe_template").read()
            shim = shim.replace("{# EXE_NAME #}", f"{self.exename}pp")
            with open(self.exepath_cpp, "w") as shim_file:
                shim_file.write(shim)
            os.chmod(self.exepath_cpp, os.stat(self.exepath_cpp).st_mode | stat.S_IEXEC)



    def clean(self):
        super().clean()
        builder_util.cleanup([
            self.intermediate_path,
            self.intermediate_path_cpp,
            f"{self.intermediate_path}.dSYM",
            f"{self.intermediate_path_cpp}.dSYM",
            self.exepath_cpp,
        ])



if "__main__" == __name__:
    b = CBuilder()

    if b.should_clean:
        b.clean()
    else:
        b.build()
