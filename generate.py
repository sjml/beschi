import os
import sys

from generator.protocol import Protocol
from generator.writers.csharp import CSharpWriter
from generator.writers.typescript import TypeScriptWriter
from generator.writers.go import GoWriter

if __name__ == "__main__":
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    p = Protocol("protocol.toml")

    out_dir = "out/csharp"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    writer = CSharpWriter()
    out = writer.generate(p)
    with open(os.path.join(out_dir, "WireMessage.cs"), "w") as o:
        o.write(out)


    out_dir = "out/typescript"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    writer = TypeScriptWriter()
    out = writer.generate(p)
    with open(os.path.join(out_dir, "WireMessage.ts"), "w") as o:
        o.write(out)


    out_dir = "out/go"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    writer = GoWriter()
    out = writer.generate(p)
    with open(os.path.join(out_dir, "WireMessage.go"), "w") as o:
        o.write(out)
