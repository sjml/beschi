import os
import subprocess
import stat

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

        if "DOTNET_VERSION" in os.environ:
            framework = f"net{os.environ['DOTNET_VERSION']}.0"
        else:
            dotnet_vers = subprocess.getoutput("dotnet --version").split(" ")[0]
            framework = f"net{'.'.join(dotnet_vers.split('.')[:-1])}"

        if builder_util.needs_build(self.intermediate_path):
            subprocess.check_call([
                "dotnet", "build",
                f"-p:SourceFile={os.path.splitext(self.srcfile)[0]}",
                f"-p:Framework={framework}",
                "-o", f"{self.intermediate_path}",
            ])

        if builder_util.needs_build(self.exepath, [self.intermediate_path]):
            shim = open("./exe_template").read()
            shim = shim.replace("{# EXE_NAME #}", self.exename)
            with open(self.exepath, "w") as shim_file:
                shim_file.write(shim)
            os.chmod(self.exepath, os.stat(self.exepath).st_mode | stat.S_IEXEC)


    def clean(self):
        super().clean()
        builder_util.cleanup([self.intermediate_path])



if "__main__" == __name__:
    b = CSharpBuilder()

    if b.should_clean:
        b.clean()
    else:
        b.build()
