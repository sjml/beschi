import os

from generator.protocol import Protocol
from generator.writers.csharp import CSharpWriter
from generator.writers.typescript import TypeScriptWriter
from generator.writers.go import GoWriter

OUTPUT_DIR = "out"
output_data = [
    (    "csharp",     CSharpWriter, "WireMessage.cs"),
    ("typescript", TypeScriptWriter, "WireMessage.ts"),
    (        "go",         GoWriter, "WireMessage.go"),
]


if __name__ == "__main__":
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    p = Protocol("./protocol.toml")

    for od in output_data:
        out_dir = os.path.join(OUTPUT_DIR, od[0])
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        writer = od[1](p)
        out = writer.generate(p)
        with open(os.path.join(out_dir, od[2]), "w") as out_file:
            out_file.write(out)
