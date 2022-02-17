LIB_NAME = "Beschi"
LIB_VERSION = "0.0.1"

import os
import sys
import argparse
import importlib

from .protocol import Protocol

writers = []
for w in os.listdir(os.path.join(os.path.abspath(os.path.dirname(__file__)), "writers")):
    if w.startswith("."): continue
    if not w.endswith(".py"): continue
    writers.append(os.path.splitext(w)[0])

def main():
    argparser = argparse.ArgumentParser(description="Generate the code for reading/writing messages from a given protocol.")
    argparser.add_argument("--lang", "-l", type=str, required=True, help="language to generate")
    argparser.add_argument("--output", "-o", type=str, default=None, help="path to output file; if omitted, will output to stdout")
    argparser.add_argument("--protocol", "-p", type=str, required=True, help="path to the protocol TOML file")

    args = argparser.parse_args()

    try:
        protocol = Protocol(args.protocol)
    except FileNotFoundError:
        sys.stderr.write(f"ERROR: No such file: {args.protocol}\n")
        sys.exit(1)
    except KeyError as ke:
        sys.stderr.write(f"ERROR: Invalid protocol file `{args.protocol}` is missing {ke}.\n")
        sys.exit(1)
    except:
        sys.stderr.write(f"ERROR: Invalid protocol file `{args.protocol}`.\n")
        sys.exit(1)

    if args.lang not in writers:
        sys.stderr.write("\n".join([
            "ERROR: invalid language. Valid writers are:",
            "\t" + ", ".join(writers),
            ""
        ]))
        sys.exit(1)

    writer_module = importlib.import_module(f".writers.{args.lang}", package="beschi")
    writer_class = getattr(writer_module, f"{writer_module.LANGUAGE_NAME}Writer")

    writer = writer_class(protocol)
    output = writer.generate()

    if args.output == None:
        print(output)
    else:
        # if there's any problem with creating/writing to this file, just let
        #    the regular exceptions bubble out
        with open(args.output, "w") as output_file:
            output_file.write(output)
