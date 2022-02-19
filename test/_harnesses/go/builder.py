import os
import subprocess
import shutil

# i hate this
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import builder_util



class GoBuilder(builder_util.Builder):
    def __init__(self) -> None:
        super().__init__("go")
        self.lib_src_dir = f"src/{self.libname}"
        self.local_libfile = os.path.join(self.lib_src_dir, self.libfile)



    def build(self):
        super().build()
        if not os.path.exists(self.lib_src_dir):
            os.makedirs(self.lib_src_dir)

        # copy the generated file in, since Go is kinda picky about include paths
        if builder_util.needs_build(self.local_libfile, [self.gen_file]):
            shutil.copy(self.gen_file, self.local_libfile)

        # build the thing
        if builder_util.needs_build(self.exepath, [self.local_libfile, self.srcfile]):
            env_copy = os.environ.copy()
            env_copy["GO111MODULE"] = "off"
            subprocess.check_call([
                "go", "build",
                "-o", self.exepath,
                self.srcfile,
            ], env=env_copy)

    def clean(self):
        super().clean()
        builder_util.cleanup([self.local_libfile])



if "__main__" == __name__:
    b = GoBuilder()

    if b.should_clean:
        b.clean()
    else:
        b.build()
