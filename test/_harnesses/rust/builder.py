import os
import subprocess
import shutil

# i hate this
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import builder_util

from beschi.writer import TextUtil


class RustBuilder(builder_util.Builder):
    def __init__(self) -> None:
        super().__init__("rust")
        self.srcfile = f"src/{self.srcfile}"
        self.local_libfiles = [f"src/{TextUtil.convert_to_lower_snake_case(lf)}" for lf in self.libfiles]



    def build(self):
        super().build()

        # copy the generated file in, since Rust is kinda picky about include paths
        for llf, gf in zip(self.local_libfiles, self.gen_files):
            if builder_util.needs_build(llf, [gf]):
                shutil.copy(gf, llf)

        # build the thing
        if builder_util.needs_build(self.exepath, [*self.local_libfiles, self.srcfile]):
            env_copy = os.environ.copy()
            env_copy["RUSTFLAGS"] = "-Dwarnings" # not a good idea in general, since it
                                                 # also breaks on dependencies, but we have none
            subprocess.check_call([
                "cargo", "build",
                "--bin", self.srcname,
            ], env=env_copy)
            shutil.copy(
                os.path.join("target", "debug", self.srcname),
                self.exepath
            )

    def clean(self):
        super().clean()
        builder_util.cleanup([*self.local_libfiles])



if "__main__" == __name__:
    b = RustBuilder()

    if b.should_clean:
        b.clean()
    else:
        b.build()
