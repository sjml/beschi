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
        self.local_libfiles = [os.path.join(self.lib_src_dir, lf) for lf in self.libfiles]


    def build(self):
        super().build()

        if not os.path.exists(self.lib_src_dir):
            os.makedirs(self.lib_src_dir)

        for llf, gf in zip(self.local_libfiles, self.gen_files):
            if builder_util.needs_build(llf, [gf]):
                shutil.copy(gf, llf)

        if builder_util.needs_build(self.intermediate_path, [*self.local_libfiles, self.srcfile]):
            subprocess.check_call([
                "swift",
                "build",
                "-Xswiftc", "-warnings-as-errors",
                # "-Xswiftc", "-warn-concurrency",
                "-Xswiftc", "-warn-implicit-overrides",
                "--product", self.srcname,
            ])

        if builder_util.needs_build(self.exepath, [self.intermediate_path]):
            shutil.copy(self.intermediate_path, self.exepath)


    def clean(self):
        super().clean()
        subprocess.check_call([
            "swift", "package", "clean"
        ])
        # if os.path.exists(self.lib_src_dir):
            # shutil.rmtree(self.lib_src_dir)


if "__main__" == __name__:
    b = SwiftBuilder()

    if b.should_clean:
        b.clean()
    else:
        b.build()
