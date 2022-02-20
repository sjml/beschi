import os
import subprocess
import shutil

# i hate this
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import builder_util



class CSharpBuilder(builder_util.Builder):
    def __init__(self) -> None:
        super().__init__("csharp")

        self.intermediate_path = os.path.join(builder_util.INTERMEDIATE_DIR, self.exename)


    def build(self):
        super().build()

        deps = [self.srcfile, self.gen_file, "harness.cs"]
        if builder_util.needs_build(self.intermediate_path, deps):
            subprocess.check_call([
                "csc", "-nologo", "-target:exe",
                f"-out:{self.intermediate_path}",
                *deps
            ])


        if builder_util.needs_build(self.exepath, [self.intermediate_path]):
            subprocess.check_call([
                "mkbundle", "--simple",
                self.intermediate_path,
                "-o", self.exepath
            ])

    def clean(self):
        super().clean()
        builder_util.cleanup([self.intermediate_path])



if "__main__" == __name__:
    b = CSharpBuilder()

    if b.should_clean:
        b.clean()
    else:
        b.build()
