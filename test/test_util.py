import os
import sys
import subprocess
import filecmp
import glob

from beschi.writer import Writer
import beschi.writers

CODE_OUTPUT_DIR = "out/generated"
DATA_OUTPUT_DIR = "out/data"
HARNESS_SRC_DIR = "test/_harnesses"
HARNESS_BIN_DIR = "out/executables"

ALL_WRITERS = beschi.writers.all_writers | beschi.writers.experimental_writers
STABLE_WRITERS = beschi.writers.all_writers
EXPERIMENTAL_WRITERS = beschi.writers.experimental_writers

def generate_for(protocol: str, output_name: str, label: str):
    writer_class = ALL_WRITERS[label]

    out_file_dir =  os.path.join(CODE_OUTPUT_DIR, label)
    out_file_path = os.path.join(out_file_dir, f"{output_name}{writer_class.default_extension}")

    if os.path.exists(out_file_path):
        os.unlink(out_file_path)
    assert(not os.path.exists(out_file_path))

    if not os.path.exists(out_file_dir):
        os.makedirs(out_file_dir)

    try:
        # using the CLI instead of calling directly to make sure everything is wired up
        subprocess.check_call(["beschi",
            "--lang", label,
            "--protocol", protocol,
            "--output", out_file_path
        ])
        assert(os.path.exists(out_file_path))
    except Exception as e:
        if label in beschi.writers.experimental_writers:
            sys.stderr.write(f"Experimental writer {label} failed while trying to produce {output_name}.\n")
            sys.stderr.write(f"Exception:\n{e.with_traceback(None)}")
        else:
            raise e

def build_for(language: str, srcfile: str, libfiles: list[str]):
    try:
        writer_class = beschi.writers.all_writers[language]
    except KeyError:
        writer_class = beschi.writers.experimental_writers[language]
    if not os.path.exists(HARNESS_BIN_DIR):
        os.makedirs(HARNESS_BIN_DIR)
    harness_path = os.path.join(HARNESS_SRC_DIR, language)
    libfile_flags = []
    for lf in libfiles:
        libfile_flags.append("--libfile")
        libfile_flags.append(f"{lf}{writer_class.default_extension}")
    invoke_build = [
        "python", f"{harness_path}/builder.py",
        "--srcfile", f"{srcfile}{writer_class.default_extension}",
        *libfile_flags
    ]
    subprocess.check_call(invoke_build + ["--clean"])
    subprocess.check_call(invoke_build)

def run_for(language: str, srcfile: str):
    if not os.path.exists(DATA_OUTPUT_DIR):
        os.makedirs(DATA_OUTPUT_DIR)

    out_file = os.path.join(DATA_OUTPUT_DIR, f"{srcfile}.{language}.msg")
    if os.path.exists(out_file):
        os.unlink(out_file)
    assert(not os.path.exists(out_file))
    subprocess.check_call([
        os.path.join(HARNESS_BIN_DIR, f"{srcfile}_{language}"),
        "--generate", out_file
    ])
    assert(os.path.exists(out_file))

    subprocess.check_call([
        os.path.join(HARNESS_BIN_DIR, f"{srcfile}_{language}"),
        "--read", out_file
    ])

    # HACKHACK
    if language == "c":
        run_for("cpp", srcfile)

def check_files_identical(data_glob):
    filecmp.clear_cache()
    messages = (glob.glob(os.path.join(DATA_OUTPUT_DIR, data_glob)))
    for i in range(len(messages)):
        j = i + 1
        if j >= len(messages):
            j -= len(messages)
        assert(filecmp.cmp(messages[i], messages[j], False))
