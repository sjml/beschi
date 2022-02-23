import os
import subprocess
import stat
import shutil

# i hate this
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import builder_util



class SwiftBuilder(builder_util.Builder):
    def __init__(self) -> None:
        super().__init__("swift")

        self.srcfile = f"Sources/{self.srcname}/main.swift"
        self.intermediate_path = f".build/debug/{self.srcname}"
        self.lib_src_dir = "Sources/GeneratedMessages"
        self.local_libfile = os.path.join(self.lib_src_dir, self.libfile)


    def build(self):
        super().build()

        if not os.path.exists(self.lib_src_dir):
            os.makedirs(self.lib_src_dir)

        if builder_util.needs_build(self.local_libfile, [self.gen_file]):
            shutil.copy(self.gen_file, self.local_libfile)

        if builder_util.needs_build(self.intermediate_path, [self.local_libfile, self.srcfile]):
            subprocess.check_call([
                "swift", "build", "--product", self.srcname
            ])

        if builder_util.needs_build(self.exepath, [self.intermediate_path]):
            shutil.copy(self.intermediate_path, self.exepath)


    def clean(self):
        super().clean()
        subprocess.check_call([
            "swift", "package", "clean"
        ])
        if os.path.exists(self.lib_src_dir):
            shutil.rmtree(self.lib_src_dir)


if "__main__" == __name__:
    b = SwiftBuilder()

    if b.should_clean:
        b.clean()
    else:
        b.build()
