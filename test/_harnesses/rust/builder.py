import os
import subprocess
import shutil

# i hate this
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import builder_util



class RustBuilder(builder_util.Builder):
    def __init__(self) -> None:
        super().__init__("rust")
        self.srcfile = f"src/{self.srcfile}"
        self.local_libfile = f"src/{self.libfile}"



    def build(self):
        super().build()

        # copy the generated file in, since Rust is kinda picky about include paths
        if builder_util.needs_build(self.local_libfile, [self.gen_file]):
            shutil.copy(self.gen_file, self.local_libfile)

        # build the thing
        if builder_util.needs_build(self.exepath, [self.local_libfile, self.srcfile]):
            subprocess.check_call([
                "cargo", "build",
                "--bin", self.srcname,
            ])
            shutil.copy(
                os.path.join("target", "release", self.srcname),
                self.exepath
            )

    def clean(self):
        super().clean()
        builder_util.cleanup([self.local_libfile])



if "__main__" == __name__:
    b = RustBuilder()

    if b.should_clean:
        b.clean()
    else:
        b.build()
