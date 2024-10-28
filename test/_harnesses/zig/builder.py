import os
import subprocess
import shutil

# i hate this
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import builder_util



class ZigBuilder(builder_util.Builder):
    def __init__(self) -> None:
        super().__init__("zig")
        self.srcfile = f"src/{self.srcfile}"
        self.local_libfiles = [f"src/lib/{lf}" for lf in self.libfiles]



    def build(self):
        super().build()

        # copy the generated file in, since Zig is a lot easier if it's one directory
        for llf, gf in zip(self.local_libfiles, self.gen_files):
            if builder_util.needs_build(llf, [gf]):
                shutil.copy(gf, llf)

        if not os.path.exists(self.srcfile):
            raise NotImplementedError(f"No existing test corresponding with \"{self.srcname}\"")

        if not os.path.exists("zig-out/bin/"):
            os.makedirs("zig-out/bin/")

        if builder_util.needs_build(self.exepath, [*self.local_libfiles, self.srcfile]):
            subprocess.check_call([
                "zig", "build-exe",
                self.srcfile,
                f"-femit-bin=zig-out/bin/{self.srcname}"
            ])
            shutil.copy(
                f"zig-out/bin/{self.srcname}",
                self.exepath
            )

    def clean(self):
        super().clean()
        builder_util.cleanup([*self.local_libfiles])


if "__main__" == __name__:
    b = ZigBuilder()

    if b.should_clean:
        b.clean()
    else:
        b.build()
