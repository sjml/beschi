import os
import subprocess
import stat

# i hate this
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import builder_util



class AssemblyScriptBuilder(builder_util.Builder):
    def __init__(self) -> None:
        super().__init__("assemblyscript")

        self.intermediate_path = f"build/{self.srcname}.wasm"
        self.node_libs = "./node_modules"


    def build(self):
        super().build()

        if builder_util.needs_build(self.node_libs):
            subprocess.check_call([
                "npm", "install"
            ])

        if builder_util.needs_build(self.intermediate_path, ["harness.mjs", "assembly/_harness.ts", f"assembly/{self.srcfile}", *self.gen_files]):
            subprocess.check_call([
                "npx", "asc", "--outFile", self.intermediate_path, f"assembly/{self.srcfile}"
            ])

        if builder_util.needs_build(self.exepath, [self.intermediate_path]):
            shim = open("./exe_template").read()
            shim = shim.replace("{# EXE_NAME #}", self.srcname)
            with open(self.exepath, "w") as shim_file:
                shim_file.write(shim)
            os.chmod(self.exepath, os.stat(self.exepath).st_mode | stat.S_IEXEC)

    def clean(self):
        super().clean()
        # builder_util.cleanup([self.node_libs, "package-lock.json"])



if "__main__" == __name__:
    b = AssemblyScriptBuilder()

    if b.should_clean:
        b.clean()
    else:
        b.build()
