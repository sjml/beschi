import os
import subprocess
import stat

# i hate this
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import builder_util



class TypeScriptBuilder(builder_util.Builder):
    def __init__(self) -> None:
        super().__init__("typescript")

        self.intermediate_path = f"{self.srcname}.js"
        self.node_libs = "./node_modules"


    def build(self):
        super().build()

        if builder_util.needs_build(self.node_libs):
            subprocess.check_call([
                "npm", "install"
            ])

        if builder_util.needs_build(self.exepath, [self.intermediate_path]):
            shim = open("./exe_template").read()
            shim = shim.replace("{# EXE_NAME #}", self.srcname)
            with open(self.exepath, "w") as shim_file:
                shim_file.write(shim)
            os.chmod(self.exepath, os.stat(self.exepath).st_mode | stat.S_IEXEC)

    def clean(self):
        super().clean()
        if os.path.exists(self.node_libs):
            subprocess.check_call([
                "npx", "tsc", "--build", "--clean"
            ])
        # builder_util.cleanup([self.node_libs, "package-lock.json"])



if "__main__" == __name__:
    b = TypeScriptBuilder()

    if b.should_clean:
        b.clean()
    else:
        b.build()
