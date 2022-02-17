import os
import sys
import importlib

# I don't like this any more than you do, but Python
#   is so weird about relative imports
os.chdir(os.path.abspath(os.path.dirname(__file__)))
os.chdir("..")
sys.path.append(os.getcwd())


from beschi.protocol import Protocol


OUTPUT_DIR = "out"
OUTPUT_BASENAME = "WireMessage"

output_data = [
    (    "CSharp", ".cs"),
    ("TypeScript", ".ts"),
    (        "Go", ".go"),
]


if __name__ == "__main__":
    p = Protocol("./test/protocols/example_protocol.toml")

    for language_name, extension in output_data:
        writer_module = importlib.import_module(f"beschi.writers.{language_name.lower()}")
        writer_class = getattr(writer_module, f"{language_name}Writer")

        out_dir = os.path.join(OUTPUT_DIR, "generated", language_name.lower())
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        writer = writer_class(p)
        out = writer.generate()
        with open(os.path.join(out_dir, f"{OUTPUT_BASENAME}{extension}"), "w") as out_file:
            out_file.write(out)
