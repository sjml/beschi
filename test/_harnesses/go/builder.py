import os
import subprocess
import shutil

# i hate this
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import builder_util

from beschi.writer import TextUtil


class GoBuilder(builder_util.Builder):
    def __init__(self) -> None:
        super().__init__("go")
        self.lib_src_dirs = [f"messages/{TextUtil.convert_to_lower_snake_case(ln)}" for ln in self.libnames]
        self.local_libfiles = [os.path.join(lsd, TextUtil.convert_to_lower_snake_case(lf)) for lsd, lf in zip(self.lib_src_dirs, self.libfiles)]



    def build(self):
        super().build()
        for lsd in self.lib_src_dirs:
            if not os.path.exists(lsd):
                os.makedirs(lsd)

        # copy the generated files in, since Go is kinda picky about include paths
        for llf, gf in zip(self.local_libfiles, self.gen_files):
            if builder_util.needs_build(llf, [gf]):
                shutil.copy(gf, llf)

        # build the thing
        if builder_util.needs_build(self.exepath, [*self.local_libfiles, self.srcfile]):
            env_copy = os.environ.copy()
            # env_copy["GO111MODULE"] = "off"
            subprocess.check_call([
                "go", "build",
                "-o", self.exepath,
            ], env=env_copy, cwd=self.srcname)

    def clean(self):
        super().clean()
        builder_util.cleanup([*self.local_libfiles])



if "__main__" == __name__:
    b = GoBuilder()

    if b.should_clean:
        b.clean()
    else:
        b.build()
