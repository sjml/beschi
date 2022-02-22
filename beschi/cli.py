import sys
import argparse

from .protocol import Protocol
from .writers import all_writers
from . import LIB_NAME, LIB_VERSION


def main():
    argparser = argparse.ArgumentParser(description="Generate the code for reading/writing messages from a given protocol.")
    argparser.add_argument("--version", "-v", action="store_const", const=True, default=False, help="print the version and exit")
    argparser.add_argument("--lang", "-l", type=str, help="language to generate")
    argparser.add_argument("--output", "-o", type=str, default=None, help="path to output file; if omitted, will output to stdout")
    argparser.add_argument("--protocol", "-p", type=str, help="path to the protocol TOML file")

    args = argparser.parse_args()

    if args.version:
        print(f"{LIB_NAME} v{LIB_VERSION}")
        sys.exit(0)

    if args.protocol == None:
        sys.stderr.write("ERROR: Missing protocol. Specify a file with '--protocol FILENAME'.")
        sys.exit(1)
    if args.lang == None:
        sys.stderr.write(f"ERROR: Missing language. Specify a language for output with '--lang {{{'|'.join(writers)}}}'.")
        sys.exit(1)

    try:
        protocol = Protocol(args.protocol)
    except FileNotFoundError:
        sys.stderr.write(f"ERROR: No such file: {args.protocol}\n")
        sys.exit(1)
    except KeyError as ke:
        sys.stderr.write(f"ERROR: Invalid protocol file '{args.protocol}' is missing {ke}.\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"ERROR: Invalid protocol file '{args.protocol}'.\n")
        sys.stderr.write(f"\t{e}\n")
        sys.exit(1)

    writers = [w.lower() for w in all_writers.keys()]
    if args.lang not in writers:
        sys.stderr.write("\n".join([
            "ERROR: invalid language. Valid writers are:",
            "\t" + ", ".join(writers),
            ""
        ]))
        sys.exit(1)

    writer_class = all_writers[args.lang]

    writer = writer_class(protocol)
    output = writer.generate()

    if args.output == None:
        print(output)
    else:
        # if there's any problem with creating/writing to this file, just let
        #    the regular exceptions bubble out
        with open(args.output, "w") as output_file:
            output_file.write(output)
