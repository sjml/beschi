import os
import platform
import subprocess

# i hate this
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import builder_util

FLAGS = [
    "-Weverything",     # actually, complain about everything
    "-Werror",          # loudly
    "-O3",              # tweak it all the way to expose any problems that arise with optimizations
    "-g"                # but be ready to debug as much as is possible
]
SILENCE_WARNINGS = [    # turn off these very specific warnings, though
    "float-equal",      # doing comparisons in the test harness; actually *do* want to to check identical
    "padded",           # automatically optimizing struct layout is a hard problem :(
    "unused-parameter", # GetSizeInBytes takes a message pointer, but never looks at it if it's constant
]
[FLAGS.append(f"-Wno-{sw}") for sw in SILENCE_WARNINGS]
CFLAGS = [
    "-std=c99",         # c99 is the baseline
    "-pedantic-errors", # complain if compiler extensions come into play
]
CSILENCE_WARNINGS = [
    "c99-extensions"    # don't get *that* pedantic
]
[CFLAGS.append(f"-Wno-{sw}") for sw in CSILENCE_WARNINGS]

CPPFLAGS = [
    "-std=c++11",       # c++11 is the baseline
]
CPPSILENCE_WARNINGS = [
    # since this code is meant to be usable from C primarily,
    #   need to silence some warnings that demand more modern C++
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

    def build(self):
        super().build()

        build_flags = FLAGS
        build_flags += [f"-I{os.path.dirname(self.gen_file)}"]
        if platform.system() == "Darwin":
            build_flags += ["-isysroot", "/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk"]

        deps = [self.srcfile, self.gen_file, "util.h"]
        if builder_util.needs_build(self.exepath, deps):
            subprocess.check_call([
                "clang", *build_flags,
                *CFLAGS,
                "-o", self.exepath,
                self.srcfile
            ])
        if builder_util.needs_build(self.exepath_cpp, deps):
            subprocess.check_call([
                "clang++", *build_flags,
                *CPPFLAGS,
                "-o", self.exepath_cpp,
                "-x", "c++", self.srcfile
            ])

    def clean(self):
        super().clean()
        builder_util.cleanup([f"{self.exepath}.dSYM", self.exepath_cpp, f"{self.exepath_cpp}.dSYM"])



if "__main__" == __name__:
    b = CBuilder()

    if b.should_clean:
        b.clean()
    else:
        b.build()
