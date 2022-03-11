import os
import stat
import platform
import subprocess
import shutil

# i hate this
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import builder_util

if platform.system() != "Windows":
    CC = os.environ.get("CC", "clang")
    CXX = os.environ.get("CXX", "clang++")

    FLAGS = [
        "-pedantic-errors", # complain if compiler extensions come into play
    ]
    # actually, complain about everything
    if CC == "clang":
        FLAGS += ["-Weverything"]
    else:
        # assuming that non-clang is GCC
        FLAGS += ["-Wall"]
    FLAGS += [
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
        "-x", "c++",        # explicitly compile C files as C++
    ]
    if CXX == "clang++":
        major_version = int(subprocess.getoutput(f"{CXX} -dumpversion").split(".")[0])
    else:
        # assuming that non-clang is GCC
        major_version = int(subprocess.getoutput(f"{CXX} -dumpversion"))

        # C++ 20 is needed to use designated initializers, but flags to indicate that shift
        if major_version <= 9:
            CPPFLAGS += ["-std=c++2a"]
        else:
            CPPFLAGS += ["-std=c++20"]
    CPPSILENCE_WARNINGS = [
        # since this code is meant to be usable from C primarily,
        #   need to silence some warnings that demand more modern C++
        "c99-extensions", # don't get *that* pedantic
        "old-style-cast", # let us use c-style casts without complaining
        "zero-as-null-pointer-constant", # otherwise have to use nullptr, or redefine it, which feels like code smell
        "cast-qual", # really wish I could only silence this for string literals
    ]
    [CPPFLAGS.append(f"-Wno-{sw}") for sw in CPPSILENCE_WARNINGS]

else:
    CC = "cl.exe"
    CXX = "cl.exe"

    FLAGS = [
        "/Wall",        # complain about everything
        "/WX",          # loudly
    ]
    SILENCE_WARNINGS = [  # turn off these very specific warnings, though
        "4100",           # unused parameter; same notes as above
        "4820",           # padding; same notes as above
        "5045",           # /Wall makes a warning about possible spectre mitigation if compiled with a specific flag?
    ]
    [FLAGS.append(f"/wd{sw}") for sw in SILENCE_WARNINGS]

    CFLAGS = [
        "/std:c11",     # <sigh> this is as low as MSVC goes :(
    ]
    CPPFLAGS = [
        "/TP",          # compile C files as C++
        "/std:c++20",   # required for designated initializers
    ]




class CBuilder(builder_util.Builder):
    def __init__(self) -> None:
        super().__init__("c")
        if self.srcfile.endswith(".h"):
            self.srcfile = f"{self.srcfile[:-2]}.c"
        self.exepath_cpp = f"{self.exepath}pp"
        self.intermediate_path = os.path.join(builder_util.INTERMEDIATE_DIR, self.exename)
        self.intermediate_path_cpp = f"{self.intermediate_path}pp"
        if platform.system() == "Windows":
            self.exepath += ".exe"
            self.exepath_cpp += ".exe"
            self.intermediate_path += ".exe"
            self.intermediate_path_cpp += ".exe"

    def build(self):
        super().build()

        build_flags = FLAGS
        if platform.system() == "Windows":
            build_flags += [f"/I{self.generated_code_dir}"]
            c_out_flags = [f"/Fe:{self.intermediate_path}", f"/Fo:{self.intermediate_path[:-4]}.obj"]
            cpp_out_flags = [f"/Fe:{self.intermediate_path_cpp}", f"/Fo:{self.intermediate_path_cpp[:-4]}.obj"]
        else:
            build_flags += [f"-I{self.generated_code_dir}"]
            if platform.system() == "Darwin":
                build_flags += ["-isysroot", "/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk"]
            c_out_flags = ["-o", self.intermediate_path]
            cpp_out_flags = ["-o", self.intermediate_path_cpp]

        deps = [self.srcfile, *self.gen_files, "util.h"]
        if builder_util.needs_build(self.intermediate_path, deps):
            subprocess.check_call([
                CC, *build_flags,
                *CFLAGS,
                *c_out_flags,
                self.srcfile
            ])
        if builder_util.needs_build(self.intermediate_path_cpp, deps):
            subprocess.check_call([
                CXX, *build_flags,
                *CPPFLAGS,
                *cpp_out_flags,
                self.srcfile
            ])

        if builder_util.needs_build(self.exepath, [self.intermediate_path]):
            if platform.system() == "Windows":
                shutil.copy(self.intermediate_path, self.exepath)
            else:
                shim = open("./exe_template").read()
                shim = shim.replace("{# EXE_NAME #}", self.exename)
                with open(self.exepath, "w") as shim_file:
                    shim_file.write(shim)
                os.chmod(self.exepath, os.stat(self.exepath).st_mode | stat.S_IEXEC)

        if builder_util.needs_build(self.exepath_cpp, [self.intermediate_path_cpp]):
            if platform.system() == "Windows":
                shutil.copy(self.intermediate_path_cpp, self.exepath_cpp)
            else:
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
